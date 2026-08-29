#!/usr/bin/env bun
/**
 * update-telos - Update TELOS life context with automatic backups and change tracking
 *
 * This command manages updates to the TELOS life context files, ensuring:
 * - Automatic timestamped backups before any modification
 * - Change tracking in updates.md
 * - Complete version history
 *
 * Usage:
 *   update-telos <file>  # reads private JSON from standard input
 *
 * Example:
 *   update-telos BOOKS.md
 *
 * Files that can be updated:
 * - BELIEFS.md - Core beliefs and world model
 * - BOOKS.md - Favorite books
 * - CHALLENGES.md - Current challenges
 * - FRAMES.md - Mental frames and perspectives
 * - GOALS.md - Life goals
 * - LESSONS.md - Lessons learned
 * - MISSION.md - Life mission
 * - MODELS.md - Mental models
 * - MOVIES.md - Favorite movies
 * - NARRATIVES.md - Personal narratives
 * - PREDICTIONS.md - Predictions about the future
 * - PROBLEMS.md - Problems to solve
 * - PROJECTS.md - Active projects
 * - STRATEGIES.md - Strategies being employed
 * - TELOS.md - Main TELOS document
 * - TRAUMAS.md - Past traumas
 * - WISDOM.md - Accumulated wisdom
 * - WRONG.md - Things I was wrong about
 */

import {
  constants,
  closeSync,
  fstatSync,
  ftruncateSync,
  lstatSync,
  mkdirSync,
  openSync,
  readFileSync,
  rmSync,
  writeSync,
  writeFileSync,
} from 'fs';
import { isAbsolute, join, relative, resolve, sep } from 'path';
import { pathToFileURL } from 'url';

export const LIFEOS_DIR = resolveLifeosDir(process.env);
const configModule = pathToFileURL(join(LIFEOS_DIR, 'TOOLS', 'LifeosConfig.ts')).href;
const { loadLifeosConfig } = await import(configModule);
const lifeosConfig = loadLifeosConfig();
export const TELOS_DIR = join(lifeosConfig.paths.userDir, 'TELOS');
const BACKUPS_DIR = join(TELOS_DIR, 'Backups');
const UPDATES_LOCK_DIR = join(TELOS_DIR, '.updates.lock');
// Changelog file: prefer whichever casing already exists (older installs used
// 'Updates.md'; the docs and scaffold use 'updates.md'), so case-sensitive
// filesystems never fork the changelog into two files (public issue #1452).
// When neither exists it is created lazily as lowercase 'updates.md'.
function hasErrorCode(error: unknown, code: string): boolean {
  return typeof error === 'object' && error !== null && Reflect.get(error, 'code') === code;
}

function ensureOwnedDirectory(path: string, create: boolean): void {
  try {
    const stat = lstatSync(path);
    if (stat.isSymbolicLink()) throw new Error(`Refusing symlinked directory: ${path}`);
    if (!stat.isDirectory()) throw new Error(`Expected directory: ${path}`);
  } catch (error) {
    if (!hasErrorCode(error, 'ENOENT') || !create) throw error;
    mkdirSync(path);
    const stat = lstatSync(path);
    if (stat.isSymbolicLink() || !stat.isDirectory()) {
      throw new Error(`Unable to create owned directory: ${path}`);
    }
  }
}

function ensureOwnedDescendant(root: string, target: string, createTarget: boolean): void {
  const relativeTarget = relative(root, target);
  if (!relativeTarget || relativeTarget === '..' || relativeTarget.startsWith(`..${sep}`) || isAbsolute(relativeTarget)) {
    throw new Error(`Configured directory must be beneath ${root}: ${target}`);
  }
  ensureOwnedDirectory(root, false);
  const components = relativeTarget.split(sep).filter(Boolean);
  let current = root;
  for (const [index, component] of components.entries()) {
    current = join(current, component);
    ensureOwnedDirectory(current, createTarget && index === components.length - 1);
  }
}

function validateTelosDirectoryOwnership(): void {
  ensureOwnedDescendant(LIFEOS_DIR, lifeosConfig.paths.userDir, false);
  ensureOwnedDescendant(LIFEOS_DIR, TELOS_DIR, true);
}

export function resolveLifeosDir(env: NodeJS.ProcessEnv): string {
  const configured = env.LIFEOS_DIR?.trim() || env.CODEX_LIFEOS_DIR?.trim();
  if (configured) return resolve(configured);
  throw new Error('LIFEOS_DIR or CODEX_LIFEOS_DIR must be set explicitly');
}

function openNoFollow(path: string, flags: number): number {
  if (typeof constants.O_NOFOLLOW !== 'number') {
    throw new Error('This platform does not support no-follow file opens');
  }
  try {
    if (lstatSync(path).isSymbolicLink()) {
      throw new Error(`Refusing to open symlink: ${path}`);
    }
  } catch (error) {
    if (!hasErrorCode(error, 'ENOENT')) throw error;
  }
  return openSync(path, flags | constants.O_NOFOLLOW, 0o600);
}

function validateUpdatesPaths(): void {
  if (typeof constants.O_NOFOLLOW !== 'number') {
    throw new Error('This platform does not support no-follow file opens');
  }
  for (const path of [join(TELOS_DIR, 'updates.md'), join(TELOS_DIR, 'Updates.md')]) {
    try {
      if (lstatSync(path).isSymbolicLink()) throw new Error(`Refusing to open symlink: ${path}`);
    } catch (error) {
      if (!hasErrorCode(error, 'ENOENT')) throw error;
    }
  }
}

function replaceFileContent(fd: number, content: string): void {
  const bytes = Buffer.from(content, 'utf-8');
  ftruncateSync(fd, 0);
  let offset = 0;
  while (offset < bytes.length) {
    offset += writeSync(fd, bytes, offset, bytes.length - offset, offset);
  }
}

function openUpdatesFile(): { created: boolean; fd: number; path: string } {
  const lower = join(TELOS_DIR, 'updates.md');
  const upper = join(TELOS_DIR, 'Updates.md');
  for (const path of [lower, upper]) {
    try {
      return { created: false, fd: openNoFollow(path, constants.O_RDWR), path };
    } catch (error) {
      if (!hasErrorCode(error, 'ENOENT')) throw error;
    }
  }
  return {
    created: true,
    fd: openNoFollow(lower, constants.O_RDWR | constants.O_CREAT | constants.O_EXCL),
    path: lower,
  };
}

// Valid TELOS files
const VALID_FILES = [
  'BELIEFS.md', 'BOOKS.md', 'CHALLENGES.md', 'FRAMES.md', 'GOALS.md',
  'LESSONS.md', 'MISSION.md', 'MODELS.md', 'MOVIES.md', 'NARRATIVES.md',
  'PREDICTIONS.md', 'PROBLEMS.md', 'PROJECTS.md', 'STRATEGIES.md',
  'TELOS.md', 'TRAUMAS.md', 'WISDOM.md', 'WRONG.md'
];

async function getTimezone(): Promise<string> {
  return lifeosConfig.principal.timezone || 'UTC';
}

async function getLocalTimestamp(): Promise<string> {
  const now = new Date();
  const timezone = await getTimezone();
  const localTime = new Date(now.toLocaleString('en-US', { timeZone: timezone }));

  const year = localTime.getFullYear();
  const month = String(localTime.getMonth() + 1).padStart(2, '0');
  const day = String(localTime.getDate()).padStart(2, '0');
  const hours = String(localTime.getHours()).padStart(2, '0');
  const minutes = String(localTime.getMinutes()).padStart(2, '0');
  const seconds = String(localTime.getSeconds()).padStart(2, '0');

  return `${year}${month}${day}-${hours}${minutes}${seconds}${String(now.getMilliseconds()).padStart(3, '0')}`;
}

async function getLocalDateForLog(): Promise<string> {
  const now = new Date();
  const timezone = await getTimezone();
  const localTime = new Date(now.toLocaleString('en-US', { timeZone: timezone }));

  const year = localTime.getFullYear();
  const month = String(localTime.getMonth() + 1).padStart(2, '0');
  const day = String(localTime.getDate()).padStart(2, '0');
  const hours = String(localTime.getHours()).padStart(2, '0');
  const minutes = String(localTime.getMinutes()).padStart(2, '0');
  const seconds = String(localTime.getSeconds()).padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds} (${timezone})`;
}

async function acquireUpdatesLock(): Promise<() => void> {
  const timeout = Number.parseInt(process.env.TELOS_UPDATES_LOCK_TIMEOUT_MS ?? '5000', 10);
  const deadline = Date.now() + (Number.isFinite(timeout) && timeout >= 0 ? timeout : 5000);
  while (true) {
    try {
      mkdirSync(UPDATES_LOCK_DIR);
      return () => rmSync(UPDATES_LOCK_DIR, { recursive: true, force: true });
    } catch (error) {
      if (!hasErrorCode(error, 'EEXIST')) throw error;
      if (Date.now() >= deadline) {
        throw new Error(
          `Timed out acquiring ${UPDATES_LOCK_DIR}; confirm no updater is running before manual recovery.`,
        );
      }
      await new Promise((resolvePromise) => setTimeout(resolvePromise, 10));
    }
  }
}

function updateTargetContent(currentContent: string, content: string): string {
  const newline = currentContent.includes('\r\n') ? '\r\n' : '\n';
  const footerMarker = `${newline}---${newline}`;
  const footerIdx = currentContent.lastIndexOf(footerMarker);
  const footer = footerIdx === -1 ? '' : currentContent.slice(footerIdx);
  const hasFooter = footerIdx !== -1 &&
    new RegExp(`${newline === '\r\n' ? '\\r\\n' : '\\n'}---${newline === '\r\n' ? '\\r\\n' : '\\n'}\\s*\\*[\\s\\S]*\\*\\s*$`).test(footer);
  const normalizedContent = content.replace(/\r?\n/g, newline);
  if (hasFooter) {
    const body = currentContent.slice(0, footerIdx).trimEnd();
    return body + newline + normalizedContent + footer;
  }
  return currentContent.trimEnd() + newline + normalizedContent + newline;
}

interface OpenBackup {
  dev: number;
  fd: number | undefined;
  filename: string;
  ino: number;
  path: string;
}

function createBackup(filename: string, currentContent: string, timestamp: string): OpenBackup {
  const stem = filename.replace('.md', `-${timestamp}`);
  for (let attempt = 0; attempt < 1000; attempt += 1) {
    const suffix = attempt === 0 ? '' : `-${attempt}`;
    const backupFilename = `${stem}${suffix}.md`;
    const backupPath = join(BACKUPS_DIR, backupFilename);
    let backupFd: number | undefined;
    try {
      backupFd = openSync(backupPath, 'wx', 0o600);
      writeFileSync(backupFd, currentContent, 'utf-8');
      const stat = fstatSync(backupFd);
      return {
        dev: stat.dev,
        fd: backupFd,
        filename: backupFilename,
        ino: stat.ino,
        path: backupPath,
      };
    } catch (error) {
      if (backupFd !== undefined) closeSync(backupFd);
      if (!hasErrorCode(error, 'EEXIST')) throw error;
    }
  }
  throw new Error(`Unable to allocate a unique backup for ${filename}`);
}

function prepareBackupStorage(): void {
  ensureOwnedDescendant(LIFEOS_DIR, BACKUPS_DIR, true);
}

function closeBackup(backup: OpenBackup, closeFile: (fd: number) => void): void {
  if (backup.fd === undefined) return;
  closeFile(backup.fd);
  backup.fd = undefined;
}

function discardBackup(backup: OpenBackup): void {
  try {
    const current = lstatSync(backup.path);
    if (current.isSymbolicLink() || current.dev !== backup.dev || current.ino !== backup.ino) {
      throw new Error(`Refusing to remove replaced backup: ${backup.path}`);
    }
    rmSync(backup.path);
  } finally {
    if (backup.fd !== undefined) closeSync(backup.fd);
    backup.fd = undefined;
  }
}

async function recordChange(filename: string, changeDescription: string, backupFilename: string): Promise<void> {
  const updatesFile = openUpdatesFile();
  let originalContent: string | undefined;
  let committed = false;
  try {
    originalContent = readFileSync(updatesFile.fd, 'utf-8');
    let updatesContent = originalContent;
    const newline = updatesContent.includes('\r\n') ? '\r\n' : '\n';
    if (updatesContent.length === 0) {
      updatesContent = ['# TELOS Updates', '', 'Changelog of TELOS file updates, newest first.', ''].join(newline);
    }
    const logTimestamp = await getLocalDateForLog();
    const logEntry = [
      '',
      `## ${logTimestamp}`,
      '',
      `- **File Modified**: ${filename}`,
      '- **Change Type**: Content Addition',
      `- **Description**: ${changeDescription}`,
      `- **Backup Location**: \`Backups/${backupFilename}\``,
      '',
    ].join(newline);

    const futureChangesMarker = '## Future Changes';
    const insertPosition = updatesContent.indexOf(futureChangesMarker);
    const firstLine = newline === '\r\n' ? /^([^\r\n]*(?:\r\n|\n))/ : /^([^\n]*\n)/;
    const updatedUpdates = insertPosition !== -1
      ? updatesContent.substring(0, insertPosition + futureChangesMarker.length) +
        updatesContent.substring(insertPosition + futureChangesMarker.length).replace(firstLine, `$1${logEntry}`)
      : updatesContent.trimEnd() + newline + logEntry;
    replaceFileContent(updatesFile.fd, updatedUpdates);
    committed = true;
  } catch (error) {
    if (originalContent !== undefined) {
      try {
        replaceFileContent(updatesFile.fd, originalContent);
      } catch (rollbackError) {
        throw new Error(`Changelog update and rollback failed: ${error}; rollback: ${rollbackError}`);
      }
    }
    throw error;
  } finally {
    closeSync(updatesFile.fd);
    if (updatesFile.created && !committed) {
      try {
        if (lstatSync(updatesFile.path).size === 0) rmSync(updatesFile.path);
      } catch (error) {
        if (!hasErrorCode(error, 'ENOENT')) throw error;
      }
    }
  }
}

function targetExisted(path: string): boolean {
  try {
    const stat = lstatSync(path);
    if (stat.isSymbolicLink()) throw new Error(`Refusing to open symlink: ${path}`);
    return true;
  } catch (error) {
    if (hasErrorCode(error, 'ENOENT')) return false;
    throw error;
  }
}

function rollbackTarget(fd: number, targetFile: string, originalContent: string, existed: boolean): void {
  replaceFileContent(fd, originalContent);
  if (!existed) rmSync(targetFile);
}

export async function main(closeBackupFile: (fd: number) => void = closeSync) {
  const args = process.argv.slice(2);

  if (args.length !== 1) {
    console.error('❌ Usage: update-telos <file>');
    console.error('\nRead JSON {"content":"...", "changeDescription":"..."} from stdin.');
    console.error('\nValid files:', VALID_FILES.join(', '));
    process.exit(1);
  }

  const [filename] = args;

  let request: { content: string; changeDescription: string };
  try {
    request = JSON.parse(readFileSync(0, 'utf-8')) as { content: string; changeDescription: string };
  } catch {
    console.error('❌ Invalid update JSON on stdin');
    process.exit(1);
  }
  const { content, changeDescription } = request;
  if (typeof content !== 'string' || !content.trim() ||
      typeof changeDescription !== 'string' || !changeDescription.trim()) {
    console.error('❌ Content and change description must be non-empty strings');
    process.exit(1);
  }

  // Validate filename
  if (!VALID_FILES.includes(filename)) {
    console.error(`❌ Invalid file: ${filename}`);
    console.error(`Valid files: ${VALID_FILES.join(', ')}`);
    process.exit(1);
  }

  validateTelosDirectoryOwnership();
  let releaseLock: (() => void);
  try {
    releaseLock = await acquireUpdatesLock();
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    console.error(`❌ Failed to acquire the TELOS changelog lock: ${detail}`);
    process.exit(1);
  }

  try {
    validateUpdatesPaths();
    // Establish the backup boundary before a missing target can be created.
    prepareBackupStorage();
    const targetFile = join(TELOS_DIR, filename);
    const existed = targetExisted(targetFile);

    // Open the target once and retain that descriptor through backup and write.
    // This prevents a path replacement between the pre-write read and mutation.
    const targetFlags = constants.O_RDWR | constants.O_CREAT;
    const targetFd = openNoFollow(targetFile, targetFlags);
    let originalContent: string | undefined;
    let backup: OpenBackup | undefined;
    try {
      originalContent = readFileSync(targetFd, 'utf-8');
      const currentContent = originalContent || `# ${filename.replace('.md', '')}\n`;
      // Step 1: Create a durable timestamped backup of the exact preimage.
      const timestamp = await getLocalTimestamp();
      backup = createBackup(filename, originalContent, timestamp);
      console.log(`✅ Backup created: ${backup.filename}`);
      closeBackup(backup, closeBackupFile);

      // Step 2: Update the target. TELOS template entries belong above the
      // italic-commentary footer; files without that shape append at EOF.
      const updatedContent = updateTargetContent(currentContent, content);
      replaceFileContent(targetFd, updatedContent);
      if (!existed) console.log(`✅ Created starter file: ${filename}`);
      console.log(`✅ Updated: ${filename}`);

      // Step 3: Record the change only after the target write. Any failure
      // rolls the target back to its exact preimage before returning.
      await recordChange(filename, changeDescription, backup.filename);
      console.log(`✅ Change logged in updates.md`);

      const backupFilename = backup.filename;
      backup = undefined;

      console.log('\n🎯 TELOS update complete!');
      console.log(`   File: ${filename}`);
      console.log(`   Backup: Backups/${backupFilename}`);
      console.log(`   Change: ${changeDescription}`);
    } catch (error) {
      let rollbackError: unknown;
      try {
        if (originalContent !== undefined) {
          rollbackTarget(targetFd, targetFile, originalContent, existed);
        } else if (!existed) {
          rmSync(targetFile);
        }
      } catch (targetRollbackError) {
        rollbackError = targetRollbackError;
      }
      if (backup !== undefined) {
        const failedBackup = backup;
        backup = undefined;
        try {
          discardBackup(failedBackup);
        } catch (backupRollbackError) {
          rollbackError = rollbackError === undefined
            ? backupRollbackError
            : `${rollbackError}; backup rollback: ${backupRollbackError}`;
        }
      }
      if (rollbackError !== undefined) {
        throw new Error(`TELOS update and rollback failed: ${error}; rollback: ${rollbackError}`);
      }
      throw new Error(`TELOS update failed without changing ${filename}: ${error}`);
    } finally {
      if (backup?.fd !== undefined) closeSync(backup.fd);
      closeSync(targetFd);
    }
  } finally {
    releaseLock();
  }
}

if (import.meta.main) {
  try {
    await main();
  } catch (error) {
    console.error(`❌ ${error instanceof Error ? error.message : String(error)}`);
    process.exitCode = 1;
  }
}

// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import fs from "node:fs/promises";
import path from "node:path";

export interface GitRepoInfo {
  owner: string;
  repo: string;
  /** Full GitHub path in "owner/repo" format */
  fullName: string;
}

interface GitContext {
  repoRoot: string;
  gitDir: string;
}

async function findGitContext(startDir = process.cwd()): Promise<GitContext> {
  let current = path.resolve(startDir);

  while (true) {
    const gitPath = path.join(current, ".git");
    try {
      const stat = await fs.stat(gitPath);
      if (stat.isDirectory()) {
        return { repoRoot: current, gitDir: gitPath };
      }

      if (stat.isFile()) {
        const pointer = (await fs.readFile(gitPath, "utf8")).trim();
        const match = pointer.match(/^gitdir:\s*(.+)$/i);
        if (!match) {
          throw new Error(`Unsupported .git file format in ${gitPath}`);
        }
        const resolvedGitDir = path.resolve(current, match[1].trim());
        return { repoRoot: current, gitDir: resolvedGitDir };
      }
    } catch {
      // Continue walking upward.
    }

    const parent = path.dirname(current);
    if (parent === current) {
      throw new Error("Not inside a git repository.");
    }
    current = parent;
  }
}

function escapeRegex(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

async function readRemoteUrl(gitDir: string, remoteName: string): Promise<string> {
  const configPath = path.join(gitDir, "config");
  const config = await fs.readFile(configPath, "utf8");

  const sectionRegex = new RegExp(
    String.raw`\[remote\s+"${escapeRegex(remoteName)}"\]([\s\S]*?)(?=\n\[|$)`,
    "m",
  );

  const sectionMatch = config.match(sectionRegex);
  if (!sectionMatch) {
    throw new Error(`Remote "${remoteName}" not found in ${configPath}`);
  }

  const urlMatch = sectionMatch[1].match(/^\s*url\s*=\s*(.+)$/m);
  if (!urlMatch) {
    throw new Error(`Remote "${remoteName}" does not define url in ${configPath}`);
  }

  return urlMatch[1].trim();
}

/**
 * Parses the current git repository's remote URL to extract owner and repo.
 * Supports both HTTPS and SSH remote URL formats.
 *
 * @param remoteName - The name of the remote to parse (default: "origin")
 * @returns The parsed repository information
 * @throws Error if not in a git repository or remote URL cannot be parsed
 */
export async function getGitRepoInfo(remoteName = "origin"): Promise<GitRepoInfo> {
  const { gitDir } = await findGitContext();
  const remoteUrl = await readRemoteUrl(gitDir, remoteName);

  return parseGitRemoteUrl(remoteUrl);
}

/**
 * Parses a git remote URL to extract owner and repo.
 * Supports both HTTPS and SSH URL formats:
 * - https://github.com/owner/repo.git
 * - git@github.com:owner/repo.git
 *
 * @param remoteUrl - The git remote URL to parse
 * @returns The parsed repository information
 * @throws Error if the URL format is not recognized
 */
export function parseGitRemoteUrl(remoteUrl: string): GitRepoInfo {
  // SSH format: git@github.com:owner/repo.git
  const sshMatch = remoteUrl.match(/git@github\.com:([^/]+)\/(.+?)(\.git)?$/);
  if (sshMatch) {
    const [, owner, repo] = sshMatch;
    return {
      owner,
      repo: repo.replace(/\.git$/, ""),
      fullName: `${owner}/${repo.replace(/\.git$/, "")}`,
    };
  }

  // HTTPS format: https://github.com/owner/repo.git
  const httpsMatch = remoteUrl.match(/https?:\/\/github\.com\/([^/]+)\/(.+?)(\.git)?$/);
  if (httpsMatch) {
    const [, owner, repo] = httpsMatch;
    return {
      owner,
      repo: repo.replace(/\.git$/, ""),
      fullName: `${owner}/${repo.replace(/\.git$/, "")}`,
    };
  }

  throw new Error(`Unable to parse git remote URL: ${remoteUrl}`);
}

/**
 * Gets the current git branch name.
 *
 * @returns The current branch name
 * @throws Error if not in a git repository
 */
export async function getCurrentBranch(): Promise<string> {
  const { gitDir } = await findGitContext();
  const head = (await fs.readFile(path.join(gitDir, "HEAD"), "utf8")).trim();

  if (head.startsWith("ref:")) {
    const ref = head.slice("ref:".length).trim();
    return path.basename(ref);
  }

  // Detached HEAD
  return head;
}

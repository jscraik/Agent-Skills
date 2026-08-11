from ask_cli_impl_tests_06 import *  # noqa: F403

class TestAskCLI(_AskCliTestBase):
    def test_plugins_init_validation_error_human_output_exposes_validation(self):
        """Verify plugins init validation errors render their replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'init', 'example-plugin', '--category', '/tmp/not-a-plugin-category', '--with-marketplace', '--with-scripts', '--robot']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Invalid plugin category', result.stdout)
        self.assertIn('Validation: ./bin/ask plugins init example-plugin --category /tmp/not-a-plugin-category --with-marketplace --with-scripts --json --robot', result.stdout)

    def test_plugins_harden_validation_error_exposes_validation(self):
        """Verify plugin harden validation errors expose a replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'harden', '/tmp/not-a-plugin', '--skip-compat', '--skip-marketplace-audit', '--no-require-marketplace', '--strict-marketplace-path', '--json', '--robot']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'error')
        self.assertEqual(output['errors'][0]['code'], 'ERR_VALIDATION')
        self.assertEqual(output['data']['validation_commands'], ['./bin/ask plugins harden /tmp/not-a-plugin --skip-compat --skip-marketplace-audit --no-require-marketplace --strict-marketplace-path --json --robot'])

    def test_plugins_harden_validation_error_human_output_exposes_validation(self):
        """Verify plugin harden validation errors render their replay command."""
        cmd = ['python3', 'Infrastructure/bin/ask', 'plugins', 'harden', '/tmp/not-a-plugin', '--skip-compat', '--skip-marketplace-audit', '--no-require-marketplace', '--strict-marketplace-path', '--robot']
        result = _run_cli(cmd)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Plugin path', result.stdout)
        self.assertIn('Validation: ./bin/ask plugins harden /tmp/not-a-plugin --skip-compat --skip-marketplace-audit --no-require-marketplace --strict-marketplace-path --json --robot', result.stdout)

__all__ = [name for name in globals() if not name.startswith("__")]

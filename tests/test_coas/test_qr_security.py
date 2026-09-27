"""
Security regression tests for qrustie binary discovery
=======================================================
These tests exist to fail loudly if the working-directory executable
search is ever reintroduced into ``find_qrustie``.

The defect: ``_QRUSTIE_SEARCH_PATHS`` contained relative paths,
including the bare name ``qrustie``, checked with ``os.path.isfile()``
against the process working directory and then handed to
``subprocess.run``. Parsing a COA from any directory an attacker could
write to would execute a file of their choosing.

Append these to tests/test_coas/test_qr.py, or keep as a separate
module. No network, no real binaries, no credentials.
"""
import os
import stat

import pytest

from cannlytics.data.coas.qr import find_qrustie

# On Windows a bare `qrustie` is not executable: the shell resolves a
# command name through PATHEXT, and the library does the same. The
# fake binaries therefore need an `.exe` there and an execute bit on
# POSIX, which is exactly what a real build produces on each platform.
BINARY_NAME = 'qrustie.exe' if os.name == 'nt' else 'qrustie'

def make_binary(path):
    """Write a fake executable at ``path`` (a directory / file name)."""
    path.write_text('#!/bin/sh\nexit 0\n')
    path.chmod(0o755)
    return path

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Fixtures                                                         ║
# ╚══════════════════════════════════════════════════════════════════╝

@pytest.fixture
def clean_env(monkeypatch):
    """Strip every environment variable that influences discovery."""
    monkeypatch.delenv('QRUSTIE_PATH', raising=False)
    monkeypatch.delenv('CANNLYTICS_QRUSTIE_ALLOW_CWD', raising=False)
    # A PATH that exists but cannot contain qrustie.
    monkeypatch.setenv('PATH', os.path.join(os.sep, 'nonexistent-path-dir'))

@pytest.fixture
def payload(tmp_path, monkeypatch):
    """An executable named `qrustie` in the working directory.

    This is the attacker's file: a COA parsed from this directory must
    never cause it to run.
    """
    binary = make_binary(tmp_path / BINARY_NAME)
    monkeypatch.chdir(tmp_path)
    return binary

@pytest.fixture
def build_tree_payload(tmp_path, monkeypatch):
    """An executable at the `qrustie/target/release/qrustie` build path."""
    target = tmp_path / 'qrustie' / 'target' / 'release'
    target.mkdir(parents=True)
    binary = make_binary(target / BINARY_NAME)
    monkeypatch.chdir(tmp_path)
    return binary

# ╔══════════════════════════════════════════════════════════════════╗
# ║ The working directory is not searched by default                 ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestCwdNotSearchedByDefault:

    def test_bare_name_in_cwd_is_ignored(self, clean_env, payload):
        """`./qrustie` must not be discovered. This is the core defect."""
        assert find_qrustie() is None

    def test_build_tree_path_in_cwd_is_ignored(self, clean_env, build_tree_payload):
        """`./qrustie/target/release/qrustie` must not be discovered."""
        assert find_qrustie() is None

    def test_allow_cwd_false_is_explicit(self, clean_env, build_tree_payload):
        assert find_qrustie(allow_cwd=False) is None

# ╔══════════════════════════════════════════════════════════════════╗
# ║ PATH entries that resolve to the working directory               ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestPathEntrySanitization:
    """An empty PATH entry means "current directory" on POSIX, and is
    exactly as dangerous as a literal `.`. `shutil.which` honours both,
    so a naive swap to `shutil.which` would NOT have closed this hole.
    """

    @pytest.mark.parametrize('path_value', [
        '/usr/bin:',        # trailing empty entry
        ':/usr/bin',        # leading empty entry
        '/usr/bin:.',       # literal dot
        '.',                # dot only
        '',                 # entirely empty
        'relative/subdir',  # non-absolute entry
    ])
    def test_relative_path_entries_are_dropped(self, monkeypatch, payload, path_value):
        monkeypatch.delenv('QRUSTIE_PATH', raising=False)
        monkeypatch.delenv('CANNLYTICS_QRUSTIE_ALLOW_CWD', raising=False)
        monkeypatch.setenv('PATH', path_value)
        assert find_qrustie() is None

    def test_missing_path_variable_is_safe(self, monkeypatch, payload):
        monkeypatch.delenv('QRUSTIE_PATH', raising=False)
        monkeypatch.delenv('CANNLYTICS_QRUSTIE_ALLOW_CWD', raising=False)
        monkeypatch.delenv('PATH', raising=False)
        assert find_qrustie() is None

    def test_absolute_path_entry_still_works(self, monkeypatch, tmp_path):
        """The legitimate case must keep working."""
        binary = make_binary(tmp_path / BINARY_NAME)
        monkeypatch.delenv('QRUSTIE_PATH', raising=False)
        monkeypatch.setenv('PATH', str(tmp_path))
        found = find_qrustie()
        assert found is not None
        assert os.path.isabs(found)
        assert os.path.samefile(found, binary)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Candidate validation                                             ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestCandidateValidation:

    @pytest.mark.skipif(os.name == 'nt', reason='POSIX execute bit')
    def test_non_executable_file_on_path_is_rejected(self, monkeypatch, tmp_path):
        """A plain text file named `qrustie` is not a binary."""
        plain = tmp_path / 'qrustie'
        plain.write_text('not a binary')
        plain.chmod(0o644)
        monkeypatch.delenv('QRUSTIE_PATH', raising=False)
        monkeypatch.setenv('PATH', str(tmp_path))
        assert find_qrustie() is None

    def test_directory_named_qrustie_is_rejected(self, monkeypatch, tmp_path):
        """A directory must never be returned as an executable."""
        (tmp_path / 'qrustie').mkdir()
        monkeypatch.delenv('QRUSTIE_PATH', raising=False)
        monkeypatch.setenv('PATH', str(tmp_path))
        assert find_qrustie() is None

    def test_returned_path_is_always_absolute(self, monkeypatch, tmp_path):
        """Nothing downstream should be able to re-resolve the path
        against a different working directory."""
        binary = make_binary(tmp_path / BINARY_NAME)
        monkeypatch.setenv('PATH', str(tmp_path))
        monkeypatch.delenv('QRUSTIE_PATH', raising=False)
        found = find_qrustie()
        assert found and os.path.isabs(found)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ The opt-in still works                                           ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestOptIn:
    """Local qrustie development must remain convenient. The point of
    the fix is to make the working-directory search deliberate, not to
    remove it.
    """

    def test_allow_cwd_finds_build_tree_binary(self, clean_env, build_tree_payload):
        found = find_qrustie(allow_cwd=True)
        assert found is not None
        assert os.path.samefile(found, build_tree_payload)

    def test_env_var_enables_cwd_search(self, clean_env, build_tree_payload,
                                        monkeypatch):
        monkeypatch.setenv('CANNLYTICS_QRUSTIE_ALLOW_CWD', '1')
        found = find_qrustie()
        assert found is not None
        assert os.path.samefile(found, build_tree_payload)

    @pytest.mark.parametrize('value', ['0', 'false', 'no', '', 'maybe'])
    def test_env_var_falsey_values_do_not_enable(self, clean_env,
                                                 build_tree_payload,
                                                 monkeypatch, value):
        monkeypatch.setenv('CANNLYTICS_QRUSTIE_ALLOW_CWD', value)
        assert find_qrustie() is None

    def test_bare_name_not_found_even_with_allow_cwd(self, clean_env, payload):
        """`allow_cwd` enables the documented build-tree paths, not a
        bare `./qrustie`. The bare name was pure liability: PATH lookup
        already covers every legitimate installed-binary case.
        """
        assert find_qrustie(allow_cwd=True) is None

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Caller-named paths take precedence                               ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestCallerNamedPaths:
    """An explicit argument and QRUSTIE_PATH are deliberate statements
    of intent, so the execute bit is not required: the operator named
    that exact file. They are still required to be regular files, and
    are still returned absolute.
    """

    def test_explicit_path_wins_over_cwd_payload(self, clean_env, payload,
                                                 tmp_path):
        real = tmp_path / 'real_qrustie'
        real.write_text('#!/bin/sh\nexit 0\n')
        real.chmod(0o755)
        found = find_qrustie(str(real))
        assert os.path.samefile(found, real)
        assert not os.path.samefile(found, payload)

    def test_env_var_path_wins_over_cwd_payload(self, clean_env, payload,
                                                tmp_path, monkeypatch):
        real = tmp_path / 'env_qrustie'
        real.write_text('wrapper script')
        monkeypatch.setenv('QRUSTIE_PATH', str(real))
        found = find_qrustie()
        assert os.path.samefile(found, real)

    def test_explicit_path_is_returned_absolute(self, clean_env, tmp_path,
                                                monkeypatch):
        real = tmp_path / 'qrustie'
        real.write_text('binary')
        monkeypatch.chdir(tmp_path)
        found = find_qrustie('qrustie')
        assert found and os.path.isabs(found)

    def test_nonexistent_explicit_path_does_not_fall_back_to_cwd(
            self, clean_env, payload):
        """A bad explicit path must not silently degrade into executing
        whatever is in the working directory."""
        assert find_qrustie('/nonexistent/qrustie') is None

    def test_explicit_directory_is_rejected(self, clean_env, tmp_path):
        d = tmp_path / 'somedir'
        d.mkdir()
        assert find_qrustie(str(d)) is None

# ╔══════════════════════════════════════════════════════════════════╗
# ║ The module no longer shells out to which/where                   ║
# ╚══════════════════════════════════════════════════════════════════╝

class TestNoShellOut:

    def test_find_qrustie_does_not_spawn_a_subprocess(self, clean_env,
                                                      monkeypatch):
        """Discovery is pure filesystem inspection. It used to spawn
        `which`/`where`, which was both slower and an extra
        partial-path execution (bandit S607).
        """
        import cannlytics.data.coas.qr as qr_module

        calls = []

        def _boom(*args, **kwargs):
            calls.append(args)
            raise AssertionError('find_qrustie must not spawn a subprocess')

        monkeypatch.setattr(qr_module.subprocess, 'run', _boom)
        find_qrustie()
        assert calls == []

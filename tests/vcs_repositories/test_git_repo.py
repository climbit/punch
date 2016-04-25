import os
import subprocess

import pytest

from punch.vcs_repositories import git_repo as gr, exceptions as re


@pytest.fixture
def temp_empty_git_dir(temp_empty_uninitialized_dir):
    subprocess.check_call(["git", "init", "-q", temp_empty_uninitialized_dir])

    return temp_empty_uninitialized_dir


@pytest.fixture
def temp_git_dir(temp_empty_git_dir):
    with open(os.path.join(temp_empty_git_dir, "README.md"), "w") as f:
        f.writelines(["# Test file", "This is just a test file for punch"])

    subprocess.Popen(["git", "add", "README.md"], cwd=temp_empty_git_dir, stdout=subprocess.DEVNULL)
    subprocess.Popen(["git", "commit", "-m", "Initial addition"], cwd=temp_empty_git_dir,
                     stdout=subprocess.DEVNULL)

    return temp_empty_git_dir


def test_get_current_branch(temp_git_dir):
    repo = gr.GitRepo(temp_git_dir)
    assert repo.get_current_branch() == 'master'


def test_get_tags(temp_git_dir):
    repo = gr.GitRepo(temp_git_dir)
    assert repo.get_tags() == ''


def test_init(temp_empty_git_dir):
    repo = gr.GitRepo(temp_empty_git_dir)

    assert repo.working_path == temp_empty_git_dir


def test_pre_start_release_with_uninitialized_directory(temp_empty_uninitialized_dir):
    repo = gr.GitRepo(temp_empty_uninitialized_dir)
    with pytest.raises(re.RepositorySystemError):
        repo.pre_start_release()


def test_pre_start_release(temp_git_dir):
    repo = gr.GitRepo(temp_git_dir)
    repo.pre_start_release()

    assert repo.get_current_branch() == 'master'


def test_pre_start_release_starting_from_different_branch(temp_git_dir):
    subprocess.Popen(["git", "checkout", "-b", "new_branch"], cwd=temp_git_dir, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)

    repo = gr.GitRepo(temp_git_dir)
    repo.pre_start_release()

    assert repo.get_current_branch() == 'master'


def test_pre_start_release_starting_from_different_branch_with_unstaged_changes(temp_git_dir):
    subprocess.Popen(["git", "checkout", "-b", "new_branch"], cwd=temp_git_dir, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    with open(os.path.join(temp_git_dir, "README.md"), "w") as f:
        f.writelines(["Unstaged lines"])

    repo = gr.GitRepo(temp_git_dir)
    repo.pre_start_release()

    assert repo.get_current_branch() == 'master'


def test_pre_start_release_starting_from_different_branch_with_uncommitted_changes(temp_git_dir):
    subprocess.Popen(["git", "checkout", "-b", "new_branch"], cwd=temp_git_dir, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    with open(os.path.join(temp_git_dir, "README.md"), "w") as f:
        f.writelines(["Unstaged lines"])
    subprocess.Popen(["git", "add", "README.md"], cwd=temp_git_dir, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)

    repo = gr.GitRepo(temp_git_dir)
    with pytest.raises(gr.RepositoryStatusError) as exc:
        repo.pre_start_release()


def test_start_release(temp_git_dir):
    repo = gr.GitRepo(temp_git_dir)
    repo.pre_start_release()
    repo.start_release("a_release")
    assert repo.get_current_branch() == "a_release"


def test_finish_release_without_changes(temp_git_dir):
    release_name = "a_release"
    repo = gr.GitRepo(temp_git_dir)
    repo.pre_start_release()
    repo.start_release(release_name)
    repo.finish_release(release_name)
    assert repo.get_current_branch() == "master"
    assert release_name not in repo.get_tags()


def test_finish_release_with_changes(temp_git_dir):
    release_name = "1.0"
    repo = gr.GitRepo(temp_git_dir)
    repo.pre_start_release()
    repo.start_release(release_name)

    with open(os.path.join(temp_git_dir, "version.txt"), "w") as f:
        f.writelines([release_name])

    repo.finish_release(release_name)
    assert repo.get_current_branch() == "master"
    assert release_name not in repo.get_tags()


def test_post_finish_release(temp_git_dir):
    release_name = "1.0"
    repo = gr.GitRepo(temp_git_dir)
    repo.pre_start_release()
    repo.start_release(release_name)
    repo.finish_release(release_name)
    repo.post_finish_release(release_name)
    assert release_name in repo.get_tags()

import os
import stat
import shutil
import logging
import subprocess

import addontools


class LibFetch:
    f"""
    Class for handling the fetching of dependencies from external repositories.\n
    `repo_path`: Path to the project, should contain the {addontools.cfg.filenames.PKGMETA_NAME} file.
    """

    def __init__(
        self, repo_path: str, svn_path: str | None = None, git_path: str | None = None
    ):
        self.repo_path = repo_path
        self.svn_path = svn_path
        self.git_path = git_path

        self.check_required_interfaces()

        self.checkout_path = os.path.join(repo_path, ".checkout")

        self.logger = logging.getLogger("addon-tools.lib-fetch")

        self.dotfile_name = addontools.cfg.filenames.PKGMETA_NAME

        self.parse_yaml()

        self.moved_files = False

    def check_required_interfaces(self):
        svn_cmd = self.svn_path or addontools.cfg.make.SVN_CMD
        git_cmd = self.git_path or addontools.cfg.make.GIT_CMD

        if not addontools.shared.interface.verify_interface(svn_cmd):
            raise EnvironmentError(f"{svn_cmd} not found or is not working correctly.")

        if not addontools.shared.interface.verify_interface(git_cmd):
            raise EnvironmentError(f"{git_cmd} not found or is not working correctly.")

    def get_meta_tag_name(self, meta: dict[str, str]) -> str:
        for key in addontools.cfg.make.META_BRANCH_KEYS:
            if key in meta:
                return key
        return ""

    def parse_yaml(self):
        yaml_file = os.path.join(self.repo_path, self.dotfile_name)
        yaml_data = addontools.yaml.YamlParser(yaml_file)

        if not yaml_data:
            raise Exception(f"Error occurred when parsing {self.dotfile_name} file.")

        self.yaml_package_as = yaml_data["package-as"]
        self.yaml_nolib_creation = yaml_data["enable-nolib-creation"]
        self.yaml_ignore = yaml_data["ignore"]
        self.yaml_externals = yaml_data["externals"]
        self.yaml_embedded_libraries = yaml_data["embedded-libraries"]
        self.yaml_manual_changelog = yaml_data["manual-changelog"]
        self.yaml_move_folders = yaml_data["move-folders"]

        self.checkout_path = os.path.join(self.checkout_path, self.yaml_package_as)  # type: ignore

    def on_rm_error(self, func, path, exc_info):
        # from: https://stackoverflow.com/questions/4829043/how-to-remove-read-only-attrib-directory-with-python-in-windows <3
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path)

    def get_name_from_url_path(self, path: str) -> str:
        if path[-1] == "/" or path[-1] == "\\":
            path = path[:-1]
        return path.split("/")[-1]

    def get_path_without_name(self, path: str) -> str:
        return "\\".join(path.split("/")[:-1])

    def rename_lib_folder(self, srcPath: str, dstPath: str) -> None:
        os.rename(srcPath, dstPath)

    def fetch_svn_repo(self, name: str, url: str):
        self.logger.info(f"Fetching {name}...")
        repo_path = os.path.join(self.checkout_path, name)

        if not os.path.exists(repo_path):
            os.makedirs(repo_path)

        command = f"{addontools.cfg.make.SVN_CMD} export {url} {repo_path} --force"
        subprocess.run(command, capture_output=True, shell=True, cwd=repo_path)
        self.logger.info(f"Successfully pulled {name}.")

    def fetch_repo(self, final_name: str, url: str | dict[str, str], repo_type: str):
        new_url = None
        branch = None
        internal_dir_name = None
        final_dir_name = self.get_name_from_url_path(final_name)
        final_dir_path = self.get_path_without_name(final_name)

        if isinstance(url, dict):
            new_url = url["url"]
            branch = url[self.get_meta_tag_name(url)]
            internal_dir_name = self.get_name_from_url_path(new_url)
        else:
            if repo_type == "git":
                internal_dir_name = self.get_name_from_url_path(url)
            else:
                internal_dir_name = final_dir_name

        self.logger.info(f"Fetching {internal_dir_name}...")
        lib_path = os.path.join(self.checkout_path, final_dir_path, internal_dir_name)
        self.logger.debug("Lib path: ", lib_path)

        if not os.path.exists(lib_path):
            os.makedirs(lib_path)

        if repo_type == "git":
            try:
                command = f"{addontools.cfg.make.GIT_CMD} clone "
                if new_url:
                    command += f"{new_url} -b {branch} "
                elif isinstance(url, str):
                    command += url

                subprocess.run(
                    command,
                    capture_output=True,
                    shell=True,
                    cwd=os.path.dirname(lib_path),
                )

                git_dir = f"{lib_path}/.git"
                github_dir = f"{lib_path}/.github"

                if os.path.exists(git_dir):
                    self.logger.debug(
                        f"Removing .git directory for {internal_dir_name}..."
                    )
                    shutil.rmtree(git_dir, onerror=self.on_rm_error)

                if os.path.exists(github_dir):
                    self.logger.debug(
                        f"Removing .github directory for {internal_dir_name}..."
                    )
                    shutil.rmtree(github_dir, onerror=self.on_rm_error)

                final_path = os.path.join(
                    self.checkout_path, final_dir_path, final_dir_name
                )
                if final_path != lib_path:
                    os.rename(lib_path, final_path)

            except FileExistsError as f:
                self.logger.critical(
                    f"Error renaming {internal_dir_name} to {final_dir_name}..."
                )
                self.logger.debug(f)
                return False

            except Exception as f:
                self.logger.error(f"Error fetching {internal_dir_name}...", exc_info=f)
                return False

        elif repo_type == "svn":
            try:
                command = f"{addontools.cfg.make.SVN_CMD} export {new_url or url} {lib_path} --force"

                subprocess.run(
                    command,
                    capture_output=True,
                    shell=True,
                    cwd=os.path.dirname(lib_path),
                )

                final_path = os.path.join(
                    self.checkout_path, final_dir_path, final_dir_name
                )
                if final_path != lib_path:
                    os.rename(lib_path, final_path)

            except FileExistsError as f:
                self.logger.critical(
                    f"Error renaming {internal_dir_name} to {final_dir_name}..."
                )
                self.logger.debug(f)
                return False

            except Exception as f:
                self.logger.error(f"Error fetching {internal_dir_name}...")
                self.logger.critical(f)
                return False

        self.logger.info(f"Successfully pulled {internal_dir_name}.")
        return True

    def get_external_libs(self):
        success = False

        if os.path.exists(os.path.join(self.repo_path, ".checkout")):
            self.logger.error(
                ".checkout folder already exists in repo root. Please remove this folder and try again."
            )
            return False

        if self.yaml_externals:
            for name, url in self.yaml_externals.items():
                if "/trunk" in url:
                    success = self.fetch_repo(name, url, "svn")
                else:
                    success = self.fetch_repo(name, url, "git")

                if not success:
                    self.logger.critical(f"Failed to fetch {name}.")
                    return False

            self.move_lib_folders()
            self.cleanup()
            self.logger.info("Lib fetching complete!")
            self.logger.warning(
                "LibFetch may leave behind extra folders in your project's lib directory. Please ensure your libs directory is clean."
            )

            return True
        else:
            self.logger.error(
                f"Lib fetching failed! External libs not found in {addontools.cfg.filenames.PKGMETA_NAME}."
            )

            return False

    def move_lib_folders(self):
        self.logger.info("Moving folders...")

        if self.yaml_ignore:
            ignore_pattern = shutil.ignore_patterns(*self.yaml_ignore)
        else:
            ignore_pattern = None

        if self.yaml_move_folders:
            for src, dest in self.yaml_move_folders.items():
                source, destination = (
                    os.path.join(self.checkout_path, src),
                    os.path.join(self.checkout_path, dest),
                )

                # copy the folders to their respective destinations from the yaml file - 'move-folders'
                if os.path.exists(source):
                    shutil.copytree(
                        source, destination, ignore=ignore_pattern, dirs_exist_ok=True
                    )
                    self.logger.info(
                        f"Successfully moved\n{source} ->\n{destination}\n"
                    )

        # copy all folders from .checkout to the repo_path, this is only done here to assist in development
        shutil.copytree(
            self.checkout_path,
            self.repo_path,
            ignore=ignore_pattern,
            dirs_exist_ok=True,
        )

        self.moved_files = True

    def cleanup(self):
        if self.moved_files:
            shutil.rmtree(os.path.dirname(self.checkout_path))
        else:
            raise Exception(
                f"Attempted to delete .checkout folder before files had been successfully moved."
            )

import os
import yaml
import shutil
import logging
import subprocess

class LibFetch:
    """
        Class for handling the fetching of dependencies from external repositories.
        `repo_path`: os.PathLike - Path to the project, should contain the .pkgmeta file.
    """
    def __init__(self, repo_path:str):
        self.repo_path = repo_path
        self.checkout_path = os.path.join(repo_path, ".checkout")

        self.logger = logging.getLogger("pkg-helper.lib-fetch")

        self.dotfile_name = ".pkgmeta"

    def parse_yaml(self) -> str:
        """Parses a .yaml file and returns some (unfortunately) hardcoded data."""
        file = os.path.join(self.repo_path, self.dotfile_name)

        with open(file, "r") as stream:
            try:
                yaml_file = yaml.safe_load(stream)  
                externals = yaml_file['externals']
                move_folders = yaml_file['move-folders']
                ignore = yaml_file['ignore']
            except Exception as exc:
                self.logger.error(exc)
                return False

        return externals, move_folders, ignore

    def fetch_curseforge_repo(self, name:str, url:str):
        self.logger.info(f"Fetching {name}...")
        repo_path = os.path.join(self.checkout_path, name)

        if not os.path.exists(repo_path):
            os.makedirs(repo_path)

        command = f"svn export {url} {repo_path} --force"
        subprocess.run(command, capture_output=True, shell=True, cwd=repo_path)
        self.logger.info(f"Successfully pulled {name}.")

    def fetch_git_repo(self, name:str, url:str):
        new_url = None
        libs_dir = "totalRP3/Libs" #FIXME: DO NOT HARD CODE THIS WTF
        lib_name = name.replace(libs_dir, "").replace(".", "-")

        if isinstance(url, dict):
            new_url = url["url"]
            branch = url["branch"]

        self.logger.info(f"Fetching {name}...")
        repo_path = os.path.join(self.checkout_path, libs_dir)

        if not os.path.exists(repo_path):
            os.makedirs(repo_path)

        try:
            command = f"git clone "
            if new_url:
                command += f"{new_url} -b {branch} "
            else:
                command += url
            subprocess.run(command, capture_output=True, shell=True, cwd=repo_path)

            git_dir = f"{repo_path}/{lib_name}/.git"

            if os.path.exists(git_dir):
                os.system(f'rmdir /S /Q "{git_dir}"')

        except Exception as f:
            self.logger.error(f)
            self.logger.error(f"Error fetching {name}...")
            return False
        self.logger.info(f"Successfully pulled {name}.")

        return True
    
    def get_external_libs(self):
        externals, move_folder, ignore = self.parse_yaml()

        if externals:
            for name, url in externals.items():
                if "curseforge" in url:
                    self.fetch_curseforge_repo(name, url)
                else:
                    self.fetch_git_repo(name, url)
            shutil.copytree(self.checkout_path, self.repo_path, dirs_exist_ok=True)
            os.system(f'rmdir /S /Q "{self.checkout_path}"')
            self.logger.info("Lib fetching complete!")
            
            return True
        else:
            self.logger.error("Parsing failed!")

            return False

if __name__ == "__main__":
    pass

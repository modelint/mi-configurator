""" config.py """

# System
import yaml
from pathlib import Path
from typing import List, Tuple, NamedTuple
import shutil

# MI Config
from exceptions import BadConfigData

# Where all app specific config files should be on linux and mac
# TODO: For Windows we use the appdirs library
user_config_home = Path.home() / ".config"

class Config:
    """
    Create an instance of this class associated with a client application

        Attributes

        - Application name -- The name of a client app that requires this configuration service
        - Lib configuration dir -- Path to a directory in the client site library where the initial config files live
        - User configuration dir -- Path to the user's custom config directory for the app
        - File names -- The names of all of the configuration files that can be loaded
        - Ext -- The file name extension for all of these files, typically 'yaml'
    """
    app_name = None
    lib_config_dir = None
    user_config_dir = None
    fnames = None
    ext = None


    def __init__(self, app_name: str, lib_config_dir: Path, fnames: Tuple[str], ext: str = "yaml"):
        """
        Config constructor - See Class comments for relevant attribute descriptions

        Saves the app name, user and library config paths, and config file names

        :param app_name: Sets Application name attribute
        :param lib_config_dir: Sets Lib configuration dir attribute
        :param fnames: Sets the configuration file names
        :param ext: The file name extension for fnames
        """
        self.user_config_dir = user_config_home / app_name  # The users's local config library for the app
        self.lib_config_dir = lib_config_dir  # The app's config library
        self.fnames = fnames  # list of file names in the app's config library
        self.ext = "." + ext  # Extension used on all of the config files

    def load(self, fnames: Tuple[str], nt_type):
        """
        Processes the config_type dictionary, loading each yaml configuration file into either
        a named tuple or a simple key value dictionary if no named tuple is provided
        and then sets the corresponding StyleDB class attribute to that value
        """
        attr_vals = dict()
        for fname in fnames:
            fpath = self.user_config_dir / (fname + self.ext)
            if nt_type:
                attr_val = self.load_yaml_to_namedtuple(fname, fpath, nt_type)
            else:
                with open(self.user_config_dir / (fname + self.ext), 'r') as file:
                    attr_val = yaml.safe_load(file)
            attr_vals[fname] = attr_val
        return attr_vals

    def reset(self, fnames: List[str] = None):
        """
        Copy user startup configuration files to their .mi_tablet/configuration dir
        Create that directory if it doesn't yet exist
        """
        user_config_path = Path.home() / self.lib_config_dir
        user_config_path.mkdir(parents=True, exist_ok=True)
        system_config_path = Path(__file__).parent / 'configuration'
        for f in system_config_path.iterdir():
            if not (user_config_path / f.name).exists():
                shutil.copy(f, user_config_path)

    def replace(self, missing_fname: str):
        """

        :param missing_fname:
        :return:
        """
        lib_source_path = self.lib_config_dir / (missing_fname + self.ext)
        self.user_config_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(lib_source_path, self.user_config_dir)

    def load_yaml_to_namedtuple(self, fname: str, file_path: Path, nt_type):
        """

        :param fname:
        :param file_path:
        :param nt_type:
        :return:
        """
        try:
            # Try to load requested file from the users's config dir
            with open(file_path, 'r') as file:
                raw_data = yaml.safe_load(file)
        except FileNotFoundError:
            # No user file, load backup from the app library config path
            self.replace(fname)
            # And try again - should succeed
            with open(file_path, 'r') as file:
                raw_data = yaml.safe_load(file)

        if not isinstance(raw_data, dict):
            raise BadConfigData(f"Expected dict when loading:\n    {file_path}")
        # Load the named tuple
        nt = {k: nt_type(**v) for k, v in raw_data.items()}
        return nt


if __name__ == "__main__":

    # See if we can load the TabletQT color.yaml file
    # Example Named tuple to test loading of color records

    class FloatRGB(NamedTuple):
        r: int
        g: int
        b: int
        canvas: bool

    # Path to the TabletQT project configuration files
    p = Path("/Users/starr/SDEV/Python/PyCharm/TabletQT/src/tabletqt/configuration")
    # Create a Config instances for the tablet app to load just the color.yaml file
    c = Config(app_name="mi_tablet", lib_config_dir=p, fnames=("colors",))
    # Load the data from the color.yaml file into a dictionary using the provided named tuple tupe
    cdata = c.load(fnames=("colors",), nt_type=FloatRGB)

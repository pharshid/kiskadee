# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import sys
import os
import tarfile
import tempfile
from shutil import copy2
import pdb
from kiskadee.helpers import to_firehose
from kiskadee.monitor import watcher
import json
import urllib.request
import pdb
from subprocess import check_output

plugin_data = {}

def setup():
    """First step to initiate the plugin life cicle.
    If your plugin does not requires some initial setup
    behavior, leave this method blank.
    """

    plugin_data = load_config(whoami())
    url = sources_gz_url(plugin_data)
    sources_gz_dir = download_sources_gz(url)
    uncompress_gz(sources_gz_dir, plugin_data['meta'])
    # Next steps
    # packages = sources_gz_to_dict(sources_gz_dir)
    # save_or_update_pkgs(packages)


def load_config(plugin):
    """Read the plugin config
    :plugin: The name of the plugin
    :returns: A dict with the plugin configuration
    """

    config_path = 'kiskadee/plugins/config.json'
    f = open(config_path, 'r')
    data = json.load(f)
    return data[plugin]


@watcher
def watch():
    #print("debian watch function")
    # setup()
    return {}

# Former watch(); this is actually analyzing the packages
def analyze(requested_source):
    """Monitor Debian repositories

    :returns: I not know yet, for now will return
    only the path to a source package, that will
    be analyzed by some analyzer.
    """

    extracts_path = extracted_source_path()
    uncompress_tar_gz(requested_source, extracts_path)
    analyzer_output = analyzers().cppcheck(extracts_path)
    to_firehose(analyzer_output, 'cppcheck')


def download_source(pkg_name, pkg_version):
    """Download packages from some debian mirror.

    :pkg_name: package name (a.g mutt)
    :pkg_version: package version (a.g 1.7.5-1)
    :returns: path to downloaded source package

    OBS: Other plugins may have this behavior,
    find a better place (module) to this method.
    """

def uncompress_tar_gz(source, path):
    """Extract the source code to a randomic dir.

    :source: The source code (tar.gz) that will be analyzed.
    :path: The path where the tar.gz is located.
    """

    copy_source(source, path)
    abs_tar_path = path + '/' + os.path.basename(source)
    source_tarfile = tarfile.open(abs_tar_path)
    source_tarfile.extractall(path)
    os.remove(abs_tar_path)

def copy_source(source, path):
    """Copy the source code to a proper directory

    :arg1: source file
    """

    source_path = abs_source_path(source)
    copy2(source_path, path)


def abs_source_path(source):
    """Returns de absolute path to the source

    :arg1: source
    :returns: path
    """
    return os.path.abspath(source)


def extracted_source_path():
    """Create a temporary directory
    """
    return tempfile.mkdtemp()

def whoami():
    """
    :returns: The plugin name

    """
    return 'debian'

def download_source(dsc_url):
    """Download packages from some debian mirror.

    :dsc_url: the url that points to some package's dsc file.
    :returns: path to downloaded source package
    """

def source_dsc_url(source_mirror, packages_gz_dict):
    """ Mount the dsc url required by dget tool to download the
    source of a debian package.

    :source_mirror: Some Debian mirror, defined on the config.json file
    :packages_gz_to_dict: A dictionary representing the Packages.gz file
    :returns: A url that points to the .dsc file of the source code,

    (a.g dget http://ftp.debian.org/debian/pool/main/0/0ad/0ad_0.0.21-2.dsc)

    """

def sources_gz_url(data):
    """ Mount the Sources.gz url"""
    mirror = data['mirror']
    release = data['release']

    return ("%s/dists/%s/main/source/Sources.gz" % (mirror, release))


def download_sources_gz(url):
    """Download and Extract the Sources.gz file, from some Debian Mirror.

    :data: The config.json file as a dict
    :returns: The path to the Packages.gz file

    """

    temp_dir = tempfile.mkdtemp()

    initial_dir = os.getcwd()
    os.chdir(temp_dir)
    in_file = urllib.request.urlopen(url)
    data = in_file.read()

    with open('Sources.gz', 'wb') as info:
        info.write(data)

    os.chdir(initial_dir)
    return temp_dir




def save_or_update_pkgs(list_of_packages):
    """Save new packages in database. If the package already exists,
    update it.

    :list_of_packages: A array with all the Packages.gz packages
    """
    pass

def sources_gz_to_dict(path):
    """Converts the Packages.gz file to a dictionary

    :path: The path to the Packages.gz file
    :returns: A dictionary representing the Packages.gz file

    """
    pass


def uncompress_gz(path, in_file):
    """Extract Some .gz file
    :returns: The path to the extracted file

    """

    compressed_file_path = os.path.join(path, in_file)
    check_output(['gzip', '-d', compressed_file_path])
    return path


def copy_source(source, path):
    """Copy the source code to a proper directory

    :arg1: source file
    """

    source_path = abs_source_path(source)
    copy2(source_path, path)


def abs_source_path(source):
    """Returns de absolute path to the source

    :arg1: source
    :returns: path
    """
    return os.path.abspath(source)


def extracted_source_path():
    """Create a temporary directory
    """
    return tempfile.mkdtemp()


def analyzers():
    """ Read wich plugins will be run on the source code

    :returns: List of plugins to run on source code.

    """
    import kiskadee.analyzers.cppcheck as cppcheck

    return cppcheck

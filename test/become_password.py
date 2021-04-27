from __future__ import absolute_import, division, unicode_literals

import textwrap
import shutil
import subprocess
import tempfile
import unittest
import configparser
import os.path
import glob
import json


class BecomePasswordTestCase(unittest.TestCase):
    workdir = None
    collection_path = None

    ansible_env = {}

    galaxy_bin = None

    inventory_bin = None
    inventory_path = None

    fixtures_path = None

    def setUp(self):
        self.workdir = tempfile.mkdtemp()
        self.collection_path = os.path.join(self.workdir, 'collections')

        collection_pattern = os.path.join(
            os.path.dirname(__file__),
            '..',
            'znerol-become_password-*.tar.gz'
        )

        # install collection
        try:
            collection_tar = glob.glob(collection_pattern)[0]
        except IndexError:
            self.fail('Collection must be built before running tests')

        self.galaxy_bin = shutil.which('ansible-galaxy')
        install_cmd = [
            self.galaxy_bin, 'collection', 'install',
            '--collections-path', self.collection_path,
            collection_tar
        ]
        subprocess.check_call(install_cmd)

        # prepare env
        env = os.environ.copy()
        env['ANSIBLE_COLLECTION_PATH'] = self.collection_path
        env['ANSIBLE_VARS_ENABLED'] = 'znerol.become_password.command'
        self.ansible_env = env

        # prepare inventory
        self.inventory_bin = shutil.which('ansible-inventory')
        inventory = textwrap.dedent('''
        some-host.example.com

        [some_group]
        other-host.example.com
        third-host.example.com
        ''')
        self.inventory_path = os.path.join(self.workdir, 'inventory')
        with open(self.inventory_path, 'w') as stream:
            print(inventory, file=stream)

        # fixtures dir
        self.fixtures_path = os.path.join(
            os.path.dirname(__file__),
            'fixtures'
        )

    def tearDown(self):
        if self.workdir is not None:
            shutil.rmtree(self.workdir)

    def testHostCommand(self):
        rev = os.path.join(self.fixtures_path, 'rev.sh')

        # ansible.cfg
        config = configparser.ConfigParser()
        config.add_section('znerol.become_password.command')
        config.set('znerol.become_password.command', 'host_command', rev)

        configpath = os.path.join(self.workdir, 'ansible.cfg')
        with open(configpath, 'w') as configfile:
            config.write(configfile)

        test_cmd = [
            self.inventory_bin,
            '--playbook-dir', self.workdir,
            '--inventory', self.inventory_path,
            '--host', 'some-host.example.com'
        ]
        stdout = subprocess.check_output(
            test_cmd,
            env=self.ansible_env,
            cwd=self.workdir
        )
        hostvars = json.loads(stdout)

        # echo some-host.example.com | rev
        self.assertEqual(
            'moc.elpmaxe.tsoh-emos', hostvars['ansible_become_password']
        )

    def testHostFail(self):
        fail = shutil.which('false')

        # ansible.cfg
        config = configparser.ConfigParser()
        config.add_section('znerol.become_password.command')
        config.set('znerol.become_password.command', 'host_command', fail)

        configpath = os.path.join(self.workdir, 'ansible.cfg')
        with open(configpath, 'w') as configfile:
            config.write(configfile)

        test_cmd = [
            self.inventory_bin,
            '--playbook-dir', self.workdir,
            '--inventory', self.inventory_path,
            '--host', 'some-host.example.com'
        ]

        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.check_call(
                test_cmd,
                env=self.ansible_env,
                cwd=self.workdir
            )

    def testGroupCommand(self):
        rev = os.path.join(self.fixtures_path, 'rev.sh')

        # ansible.cfg
        config = configparser.ConfigParser()
        config.add_section('znerol.become_password.command')
        config.set('znerol.become_password.command', 'group_command', rev)

        configpath = os.path.join(self.workdir, 'ansible.cfg')
        with open(configpath, 'w') as configfile:
            config.write(configfile)

        test_cmd = [
            self.inventory_bin,
            '--playbook-dir', self.workdir,
            '--inventory', self.inventory_path,
            '--host', 'other-host.example.com'
        ]
        stdout = subprocess.check_output(
            test_cmd,
            env=self.ansible_env,
            cwd=self.workdir
        )
        hostvars = json.loads(stdout)

        # echo some_group | rev
        self.assertEqual(
            'puorg_emos', hostvars['ansible_become_password']
        )

    def testAllGroupCommand(self):
        rev = os.path.join(self.fixtures_path, 'rev.sh')

        # ansible.cfg
        config = configparser.ConfigParser()
        config.add_section('znerol.become_password.command')
        config.set('znerol.become_password.command', 'group_command', rev)

        configpath = os.path.join(self.workdir, 'ansible.cfg')
        with open(configpath, 'w') as configfile:
            config.write(configfile)

        test_cmd = [
            self.inventory_bin,
            '--playbook-dir', self.workdir,
            '--inventory', self.inventory_path,
            '--host', 'some-host.example.com'
        ]
        stdout = subprocess.check_output(
            test_cmd,
            env=self.ansible_env,
            cwd=self.workdir
        )
        hostvars = json.loads(stdout)

        # echo ungrouped | rev
        self.assertEqual(
            'depuorgnu', hostvars['ansible_become_password']
        )

    def testGroupFail(self):
        fail = shutil.which('false')

        # ansible.cfg
        config = configparser.ConfigParser()
        config.add_section('znerol.become_password.command')
        config.set('znerol.become_password.command', 'group_command', fail)

        configpath = os.path.join(self.workdir, 'ansible.cfg')
        with open(configpath, 'w') as configfile:
            config.write(configfile)

        test_cmd = [
            self.inventory_bin,
            '--playbook-dir', self.workdir,
            '--inventory', self.inventory_path,
            '--host', 'other-host.example.com'
        ]

        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.check_call(
                test_cmd,
                env=self.ansible_env,
                cwd=self.workdir
            )

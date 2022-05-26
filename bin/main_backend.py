import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

import os
from pathlib import Path

from bin.utils import *
from bin import ui_about, ui_settings

HOST_IP = "0.0.0.0"
LOCAL_HOST_IP = get_local_ip()
config_vars = get_config_variables()
FTP_PORT = 2121


class FTPServerWorker(QThread):

    def __init__(self):

        super(FTPServerWorker, self).__init__()

    def __del__(self):
        self.exiting = True
        self.wait()

        # self.server.close_when_done()
        # self.server.close()

    def run(self):
        # Instantiate a dummy authorizer for managing 'virtual' users
        authorizer = DummyAuthorizer()

        # Define a new user having full r/w permissions and a read-only
        # anonymous user
        authorizer.add_user('user', '12345', config_vars['FTP_DIR'], perm='elradfmwMT')
        authorizer.add_anonymous(config_vars['FTP_DIR'])

        # Instantiate FTP handler class
        handler = MyFTPHandler
        handler.authorizer = authorizer

        # Define a customized banner (string returned when client connects)
        handler.banner = "pyftpdlib based ftpd ready."

        # Instantiate FTP server class and listen on 0.0.0.0:2121
        address = (config_vars['HOST_IP'], config_vars['FTP_PORT'])
        self.server = FTPServer(address, handler)

        # set a limit for connections
        self.server.max_cons = 256
        self.server.max_cons_per_ip = 5

        # start ftp server
        print(f"[FTP SERVER START] Starting FTP server on {LOCAL_HOST_IP}:{config_vars['FTP_PORT']}")
        self.server.serve_forever()

    def stop(self):
        self.server.close_all()


class MyFTPHandler(FTPHandler):

    def on_connect(self):
        print(f"[FTP CONNECT] New connection [{self.remote_ip}:{self.remote_port}]")

    def on_disconnect(self):
        # do something when client disconnects
        print(f"[FTP DISCONNECT] User [{self.remote_ip}:{self.remote_port}] Disconnected")

    def on_login(self, username):
        # do something when user login
        print(f"[FTP LOGIN] New user logged in => {username}@[{self.remote_ip}:{self.remote_port}]")

    def on_logout(self, username):
        # do something when user logs out
        print(f"[FTP LOGOUT] User {username} logged out => [{self.remote_ip}:{self.remote_port}]")

    def on_file_sent(self, file):
        # do something when a file has been sent
        print(f"[FTP FILE SENT] Sent a file <{file}> => [{self.remote_ip}:{self.remote_port}")

    def on_file_received(self, file):
        # do something when a file has been received
        print(f"[FTP FILE RECEIVED] New file received <{file}> => [{self.remote_ip}:{self.remote_port}")

    def on_incomplete_file_sent(self, file):
        # do something when a file is partially sent
        print(f"[FTP INCOMPLETE SENT FILE] <{file}> => [{self.remote_ip}:{self.remote_port}")

    def on_incomplete_file_received(self, file):
        # remove partially uploaded files
        print(f"[FTP INCOMPLETE RECEIVED FILE] <{file}> => [{self.remote_ip}:{self.remote_port}")


class AboutApp(QDialog):

    def __init__(self):

        super().__init__()
        self.ui = ui_about.Ui_Dialog()
        self.ui.setupUi(self)


class SettingsApp(QDialog):

    def __init__(self, restart_callback):

        super().__init__()
        self.ui = ui_settings.Ui_Dialog()
        self.ui.setupUi(self)

        ## Variables
        self.restart_callback = restart_callback

        ## Connections
        self.ui.browse_button.clicked.connect(self.open_dir_dialog)

        ## Setup
        self.init_setup()

    def init_setup(self):

        number_validator = QIntValidator()
        self.ui.port_number_edit.setValidator(number_validator)

        self.ui.base_dir_edit.setText(str(config_vars['FTP_DIR']))
        self.ui.port_number_edit.setText(str(config_vars['FTP_PORT']))

    def open_dir_dialog(self):
        """
        Opens the explorer to browse for server base directory
        :return:
        """

        if os.path.isdir(config_vars['FTP_DIR']):
            default_browser_dir = config_vars['FTP_DIR']
        else:
            default_browser_dir = Path.home()

        dri_path = QFileDialog.getExistingDirectory(directory=default_browser_dir, caption="Select a directory to server using the server")

        if dri_path.strip() == '':
            return

        config_vars['FTP_DIR'] = dri_path

        dump_new_settings(config_vars)

        self.ui.base_dir_edit.setText(str(config_vars['FTP_DIR']))

        self.restart_callback()

    def save_settings(self):
        """
        Saves the ui filled settings onto disk on the config json file
        :return:
        """
        pass

    def get_init_settings(self):
        """
        Function to get the settings from the config file and fill them onto the settings ui
        :return:
        """

        pass



















































































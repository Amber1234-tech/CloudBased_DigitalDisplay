#!/bin/bash
#connect to the onedrive

rclone --vfs-cache-mode writes mount pi-onedrive: ~/OneDrive

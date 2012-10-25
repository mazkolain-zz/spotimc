'''
Copyright 2011 Mikel Azkolain

This file is part of Spotimc.

Spotimc is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Spotimc is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Spotimc.  If not, see <http://www.gnu.org/licenses/>.
'''


import os
import fnmatch
import xml.etree.ElementTree as ET
import zipfile


#Get the working dir of the script
work_dir = os.getcwd()


include_files = [
    'resources/*',
    'addon.xml',
    'changelog.txt',
    'default.py',
    'envutils.py',
    'icon.png',
    'LICENSE.txt',
    'README.md',
]

exclude_files = [
    '*.pyc',
    '*.pyo',
    '*/Thumbs.db',
    'resources/libs/spotimcgui/appkey.py-template',
]


def get_addon_info():
    path = os.path.join(work_dir, 'addon.xml')
    root = ET.parse(path).getroot()
    return root.attrib['id'], root.attrib['version']


def is_included(path): 
    for item in include_files:
        #Try fnmatching agains the include rule
        if fnmatch.fnmatch(path, item):
            return True
        
        #Also test if it gets included by a contained file
        elif path.startswith(item):
            return True
        
        #Or if the path is part of a pattern
        elif item.startswith(path):
            return True


def is_excluded(path):
    for item in exclude_files:
        #Try fnmatching agains the exclude entry
        if fnmatch.fnmatch(path, item):
            return True


def generate_file_list(path):
    file_list = []
    
    for item in os.listdir(path):
        cur_path = os.path.join(path, item)
        cur_rel_path = os.path.relpath(cur_path, work_dir)
         
        if is_included(cur_rel_path) and not is_excluded(cur_rel_path):
            file_list.append(cur_rel_path)
            
            if os.path.isdir(cur_path):
                file_list.extend(generate_file_list(cur_path))
        
    return file_list


def create_build_dir():
    build_dir = os.path.join(work_dir, 'build')
    if not os.path.isdir(build_dir):
        os.mkdir(build_dir)
    return build_dir


def generate_zip(build_dir, addon_id, addon_version, file_list):
    #for item in file_list:
    #    print item
    zip_name = '%s-%s.zip' % (addon_id, addon_version)
    zip_path = os.path.join(build_dir, zip_name)
    zip_obj = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    
    for item in file_list:
        abs_path = os.path.join(work_dir, item)
        if not os.path.isdir(abs_path):
            arc_path = os.path.join(addon_id, item)
            zip_obj.write(abs_path, arc_path)
    
    zip_obj.close()
    
    return zip_path


def main():
    build_dir = create_build_dir()
    addon_id, addon_version = get_addon_info()
    file_list = generate_file_list(work_dir)
    out_file = generate_zip(build_dir, addon_id, addon_version, file_list)
    print 'generated zip: %s' % os.path.relpath(out_file, work_dir)


if __name__ == '__main__':
    main()

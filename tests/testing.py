# -*- coding: utf-8 -*-
"""
Test the tex_tools functionality.
"""


# Python imports.
import unittest
import os
import shutil

# Import text tools functions.
from tex_tools import LaTeXFile


class TestTexTools(unittest.TestCase):
    """Test various stuff from the tex_tools module."""

    def test_replace_command(self):
        """
        Test the replace command functionality.
        """

        # Copy the files to the testing directory.
        testing_ref = 'reference_files'
        testing_temp = 'testing_tmp'
        os.makedirs(testing_temp, exist_ok=True)
        if os.path.isdir(testing_temp):
            for the_file in os.listdir(testing_temp):
                file_path = os.path.join(testing_temp, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(e)
        files = [
            'main',
            'shortcuts',
            'text'
            ]
        for file in files:
            shutil.copyfile(
                os.path.join(testing_ref, file + '.tex'),
                os.path.join(testing_temp, file + '.tex'))

        # Replace commands.
        def load_file():
            return LaTeXFile(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    testing_temp, files[0] + '.tex'),
                recursive=True)

        tex_file = load_file()
        tex_file.replace('tns', 'newCommand', dry_run=False, verbose=False)

        tex_file = load_file()
        tex_file.replace('tns', 'newCommand', dry_run=False, verbose=False)

        tex_file = load_file()
        tex_file.replace('tnss', 'newerCommand', dry_run=False, verbose=False)

        tex_file = load_file()
        tex_file.replace('tnss', 'newerCommand', dry_run=False, verbose=False)

        tex_file = load_file()
        tex_file.replace('tns', 'newCommand', dry_run=False, verbose=False)

        tex_file = load_file()
        tex_file.replace('tnss', 'newerCommand', dry_run=False, verbose=False)

        # Compare the replaced files.
        for file in files:
            with open(os.path.join(testing_ref, file + '_ref.tex'),
                    'r') as tex_file:
                ref_data = tex_file.read()
            with open(os.path.join(testing_temp, file + '.tex'),
                    'r') as tex_file:
                test_data = tex_file.read()
            self.assertTrue(ref_data == test_data)


if __name__ == '__main__':
    # Execution part of script.

    # Perform the tests.
    unittest.TextTestRunner().run(
        unittest.TestLoader().loadTestsFromTestCase(TestTexTools))

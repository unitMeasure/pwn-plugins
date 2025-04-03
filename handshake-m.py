import logging
import os
import glob
import zipfile
from io import BytesIO

import pwnagotchi
import pwnagotchi.plugins as plugins

from flask import redirect, send_from_directory, render_template_string, send_file

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Handshakes Manager</title>
    <style>
        .files {
            display: none;
        }
        .arrow {
            cursor: pointer;
        }
    </style>
    <script>
        function toggleFiles(ssid) {
            var filesDiv = document.getElementById(ssid);
            var arrow = document.getElementById("arrow-" + ssid);
            if (filesDiv.style.display === "none" || filesDiv.style.display === "") {
                filesDiv.style.display = "table-row-group";  // this is the default display for tbody
                arrow.innerHTML = "&#9660;"; // Down arrow
            } else {
                filesDiv.style.display = "none";
                arrow.innerHTML = "&#9658;"; // Right arrow
            }
        }
        function filterTable() {
            var input, filter, table, tr, td, i, j, txtValue;
            input = document.getElementById("searchBar");
            filter = input.value.toUpperCase();
            table = document.getElementById("handshakeTable");
            tr = table.getElementsByTagName("tbody"); // Get tbody elements (where data is stored)
            
            for (i = 0; i < tr.length; i+=2) { // Increment by 2 because of the structure
                td = tr[i].getElementsByTagName("td")[0];
                if (td) {
                    txtValue = td.textContent || td.innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        tr[i].style.display = "";
                        tr[i+1].style.display = tr[i+1].style.display === "table-row-group" ? "table-row-group" : "none"; 
                    } else {
                        tr[i].style.display = "none";
                        tr[i+1].style.display = "none";
                    }
                }       
            }
        }
    </script>
    
</head>
<body>
    <div style="margin-bottom: 20px;">
        <a href="/">Home</a> |
        <a href="/plugins">Plugins</a>
    </div>
    
    <h1>Handshakes</h1>
    <input type="text" id="searchBar" onkeyup="filterTable()" placeholder="Search for handshakes...">
    <table id="handshakeTable">
        <thead>
            <tr>
                <th>Handshake File</th>
                <th>Action</th>
            </tr>
        </thead>
        {% for ssid, files in handshakes.items() %}
        <tbody>
            <tr>
                <td><span class="arrow" id="arrow-{{ ssid }}" onclick="toggleFiles('{{ ssid }}')">&#9658;</span> {{ ssid }}</td>
                <td>
                    <a href="/plugins/handshakes-dl/download-all/{{ ssid }}">Download All</a> | 
                    <a href="/plugins/handshakes-dl/delete/{{ ssid }}" onclick="return confirm('Are you sure you want to delete all files for this SSID?');">Delete All</a>
                </td>
            </tr>
        </tbody>
        <tbody class="files" id="{{ ssid }}">
            {% for file in files %}
            <tr>
                <td>- {{ file }}</td>
                <td>
                    <a href="/plugins/handshakes-dl/download/{{ file }}">Download</a> |
                    <a href="/plugins/handshakes-dl/delete/{{ file }}" onclick="return confirm('Are you sure you want to delete this file?');">Delete</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
        {% endfor %}
    </table>
</body>
</html>
"""

class HandshakesManager(plugins.Plugin):
    __author__ = 'retiolus'
    __version__ = '1.1.2'
    __license__ = 'GPL3'
    __description__ = 'A plugin for Pwnagotchi to view and manage handshake captures via web UI.'

    def on_loaded(self):
        try:
            logging.info("[Handshakes Manager]  plugin loaded")
        except Exception as e:
            logging.error(f"[Handshakes Manager] Error occurred in on_loaded: {str(e)}")

    def on_config_changed(self, config):
        self.config = config

    def on_webhook(self, path, request):
        try:
            logging.error(f"[Handshakes Manager] {path}")
            if path == "/" or not path:
                handshakes = glob.glob(os.path.join(self.config["bettercap"]["handshakes"], "*"))
                handshakes_dict = {}
                for handshake in handshakes:
                    ssid = os.path.basename(handshake).split('.')[0]
                    if ssid not in handshakes_dict:
                        handshakes_dict[ssid] = []
                    handshakes_dict[ssid].append(os.path.basename(handshake))
                
                sorted_handshakes = dict(sorted(handshakes_dict.items()))
                return render_template_string(TEMPLATE, title="Handshakes", handshakes=sorted_handshakes)

            elif path.startswith("delete/"):
                handshake_name = path.split("delete/")[1]
                self.delete_handshake(handshake_name)
                return redirect("/plugins/handshakes-dl/")

            elif path.startswith("download/"):
                dir = self.config["bettercap"]["handshakes"]
                handshake_filename = os.path.basename(path.split("download/")[1])
                logging.info(f"[Handshakes Manager] serving {dir}/{handshake_filename}")
                return send_from_directory(directory=dir, path=handshake_filename, as_attachment=True)

            elif path.startswith("download-all/"):
                ssid = path.split("download-all/")[1]
                files_for_ssid = glob.glob(os.path.join(self.config["bettercap"]["handshakes"], ssid + "*"))
                if not files_for_ssid:
                    logging.error(f"[Handshakes Manager] No files found for SSID {ssid}")
                    abort(400)

                memory_file = BytesIO()
                with zipfile.ZipFile(memory_file, 'w') as zf:
                    for file_path in files_for_ssid:
                        zf.write(file_path, os.path.basename(file_path))
                memory_file.seek(0)

                return send_file(memory_file, attachment_filename=f'{ssid}.zip', as_attachment=True)

        except FileNotFoundError:
            logging.error(f"[Handshakes Manager] File {path} not found")
            abort(400)
        except Exception as e:
            logging.error(f"[Handshakes Manager] An unexpected error occurred: {str(e)}")
            abort(500)

    def delete_handshake(self, handshake_name):
        files_to_delete = glob.glob(os.path.join(self.config["bettercap"]["handshakes"], handshake_name + "*"))
        for file_path in files_to_delete:
            logging.info(f"[Handshakes Manager] deleting {file_path}")
            try:
                os.remove(file_path)
                logging.info(f"[Handshakes Manager] Deleted {file_path}")
            except FileNotFoundError:
                logging.warning(f"[Handshakes Manager] File {file_path} not found")
            except Exception as e:
                logging.error(f"[Handshakes Manager] Error deleting file {file_path}: {str(e)}")
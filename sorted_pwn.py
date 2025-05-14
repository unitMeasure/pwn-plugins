import logging
import json
import os
import glob

import pwnagotchi.plugins as plugins

from flask import abort
from flask import send_from_directory
from flask import render_template_string

TEMPLATE = """
{% extends "base.html" %}
{% set active_page = "passwordsList" %}

{% block title %}
    {{ title }}
{% endblock %}

{% block meta %}
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, user-scalable=0" />
{% endblock %}

{% block styles %}
{{ super() }}
    <style>

        #searchText {
            width: 100%;
        }

        table {
            table-layout: auto;
            width: 100%;
        }

        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
        }

        th, td {
            padding: 15px;
            text-align: left;
        }

        table tr:nth-child(even) {
            background-color: #eee;
        }

        table tr:nth-child(odd) {
            background-color: #fff;
        }

        table th {
            background-color: black;
            color: white;
        }

        @media screen and (max-width:700px) {
            table, tr, td {
                padding:0;
                border:1px solid black;
            }

            table {
                border:none;
            }

            tr:first-child, thead, th {
                display:none;
                border:none;
            }

            tr {
                float: left;
                width: 100%;
                margin-bottom: 2em;
            }

            table tr:nth-child(odd) {
                background-color: #eee;
            }

            td {
                float: left;
                width: 100%;
                padding:1em;
            }

            td::before {
                content:attr(data-label);
                word-wrap: break-word;
                background-color: black;
                color: white;
                border-right:2px solid black;
                width: 20%;
                float:left;
                padding:1em;
                font-weight: bold;
                margin:-1em 1em -1em -1em;
            }
        }
    </style>
{% endblock %}
{% block script %}
    var searchInput = document.getElementById("searchText");
    searchInput.onkeyup = function() {
        var filter, table, tr, td, i, j, txtValue, rowContainsFilter;
        filter = searchInput.value.toUpperCase();
        table = document.getElementById("tableOptions");
        if (table) {
            tr = table.getElementsByTagName("tr");

            for (i = 0; i < tr.length; i++) {
                // Skip header rows if they exist and you don't want to filter them
                // For example, if your header is in a <thead>, you could get rows from <tbody> instead
                // Or check if tr[i].parentNode.tagName === 'THEAD' and continue

                rowContainsFilter = false; // Flag to check if any td in the current row matches
                tds = tr[i].getElementsByTagName("td");

                for (j = 0; j < tds.length; j++) {
                    let currentTd = tds[j];
                    if (currentTd) {
                        txtValue = currentTd.textContent || currentTd.innerText;
                        if (txtValue.toUpperCase().indexOf(filter) > -1) {
                            rowContainsFilter = true;
                            break; // Found a match in this row, no need to check other tds
                        }
                    }
                }

                if (rowContainsFilter) {
                    tr[i].style.display = "";
                } else {
                    // Only hide if it's not a header row (th)
                    // This check is basic, if you have th in tbody, you might need a more specific check
                    if (tr[i].getElementsByTagName("th").length === 0) {
                        tr[i].style.display = "none";
                    }
                }
            }
        }
    }

{% endblock %}

{% block content %}
    <input type="text" id="searchText" placeholder="Search for ..." title="Type in a filter">
    <table id="tableOptions">
        <tr>
            <th>SSID</th>
            <th>Password</th>
        </tr>
        {% for p in passwords %}
            <tr>
                <td data-label="SSID">{{p["ssid"]}}</td>
                <td data-label="Password">{{p["password"]}}</td>
            </tr>
        {% endfor %}
    </table>
{% endblock %}
"""

class sorted_pwn(plugins.Plugin):
    __author__ = '37124354+dbukovac@users.noreply.github.com edited by avipars'
    __version__ = '0.0.2.1'
    __license__ = 'GPL3'
    __description__ = 'List cracked passwords from any potfile found in the handshakes directory'
    __github__ = 'https://github.com/evilsocket/pwnagotchi-plugins-contrib/blob/df9758065bd672354b3fa2a3299f4a8d80c8fd6a/wpa-sec-list.py'
    def __init__(self):
        self.ready = False

    def on_loaded(self):
        logging.info("[sorted_pwn] plugin loaded")

    def on_config_changed(self, config):
        self.config = config
        self.ready = True

    def on_webhook(self, path, request):
        if not self.ready:
            return "Plugin not ready"

        if path == "/" or not path:
            try:
                base_dir = self.config['bettercap']['handshakes']
                potfile_paths = glob.glob(os.path.join(base_dir, "*.potfile"))
            
                unique_entries = {}
                for pf_path in potfile_paths:
                    logging.info("[sorted_pwn] trying to open %s" % pf_path)
                    with open(pf_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            line = line.strip()
                            if not line or ":" not in line:
                                continue
                            fields = line.split(":")
                            if len(fields) < 2:
                                continue

                            # to deal with both pwncrack and wpa-sec format
                            ssid = fields[-2].strip()
                            password = fields[-1].strip()

                            key = (ssid, password)
                            if key not in unique_entries:
                                unique_entries[key] = {
                                    "ssid": ssid,
                                    "password": password
                                }

                # Convert to sorted list
                sorted_passwords = sorted(unique_entries.values(), key=lambda x: (x["ssid"].lower(), x["password"]))

                return render_template_string(TEMPLATE,
                                            title="Unique Passwords List",
                                            passwords=sorted_passwords)
            except Exception as e:
                logging.error("[sorted_pwn] error while loading potfiles: %s" % e)
                logging.debug(e, exc_info=True)
                abort(500)
import logging
import os
import glob
import pwnagotchi.plugins as plugins
from flask import abort, send_from_directory, render_template_string, request, make_response

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
    <div style="margin-bottom:10px;">
    Sort:
    {% if order == "asc" %}
        <strong>Ascending</strong> |
        <a href="?order=desc">Descending</a>
    {% else %}
        <a href="?order=asc">Ascending</a> |
        <strong>Descending</strong>
    {% endif %}
    |
    <a href="?order={{ order }}&export=1">Export Results</a>
    </div>
    <table id="tableOptions">
        <tr>
            <th>SSID</th>
            <th>Password</th>
            <th>Other</th>
        </tr>
        {% for p in passwords %}
            <tr>
                <td data-label="SSID">{{p["ssid"]}}</td>
                <td data-label="Password">{{p["password"]}}</td>
                <td data-label="Other">
                    {% set other = p.get("other_fields") %}
                    {% if other %}
                        {% if other is iterable and other is not string %}
                            {{ other | join(", ") }}
                        {% else %}
                            {{ other }}
                        {% endif %}
                    {% else %}
                        <span>None</span>
                    {% endif %}
                </td>
            </tr>
        {% endfor %}
    </table>
{% endblock %}
"""

class sorted_pwn(plugins.Plugin):
    __author__ = '37124354+dbukovac@users.noreply.github.com'
    __editor__ = 'avipars'
    __version__ = '0.0.3'
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

    def decode_hex_field(self, value):
        """Decode hashcat/potfile $HEX[...] encoded fields to a UTF-8 string.
        Falls back to the original value if decoding fails."""
        if isinstance(value, str) and value.startswith("$HEX[") and value.endswith("]"):
            hex_str = value[5:-1]
            try:
                return bytes.fromhex(hex_str).decode("utf-8", errors="replace")
            except ValueError:
                return value    # Not valid hex , leave as-is
        return value

    def on_webhook(self, path, request):
        if not self.ready:
            return "Plugin not ready"

        if path == "/" or not path:
            try:
                order = request.args.get("order", "asc").lower()
                reverse_sort = order == "desc"
                export = request.args.get("export", "0") == "1"
                show_other = request.args.get("show_other", "0") == "1" # TODO hide other fields in table if user wants
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
                            ssid = self.decode_hex_field(fields[-2].strip())      # 2nd to last
                            password = self.decode_hex_field(fields[-1].strip()) # last one
                            other_fields = fields[:-2]   # everything before ssid/password (bssid, client)

                            key = (ssid, password)
                            if key not in unique_entries:
                                unique_entries[key] = {
                                    "ssid": ssid,
                                    "password": password,
                                    "other_fields": other_fields,   # list of other fields usually bssid etc.
                                }
                            else: # keep additional occurrences if you want
                                unique_entries[key].setdefault("duplicates", []).append({ 
                                    "other_fields": other_fields   
                                })

                sorted_passwords = sorted(unique_entries.values(), key=lambda x: (x["ssid"].lower(), x["password"]), reverse=reverse_sort)  # Convert to sorted list

                html = render_template_string(
                    TEMPLATE,
                    title="Unique Passwords List",
                    passwords=sorted_passwords,
                    order=order
                )

                if export:
                    lines = []
                    lines.append("SSID\tPassword\tOther")

                    for p in sorted_passwords:

                        if show_other:
                            other = p.get("other_fields")
                            if isinstance(other, list):
                                other = ", ".join(other)

                            lines.append(
                                "%s:%s:%s" % (
                                    p.get("ssid", ""),
                                    p.get("password", ""),
                                    other or ""
                                )
                            )
                        else:
                                lines.append(
                                "%s:%s" % (
                                    p.get("ssid", ""),
                                    p.get("password", ""),
                                )
                            )

                    txt_data = "\n".join(lines)

                    response = make_response(txt_data)
                    response.headers["Content-Type"] = "text/plain; charset=utf-8"
                    response.headers["Content-Disposition"] = (
                        "attachment; filename=sorted_pwn_passwords_%s.txt" % order
                    )
                    return response
                return html

              
            except Exception as e:
                logging.error("[sorted_pwn] error while loading potfiles: %s" % e)
                logging.debug(e, exc_info=True)
                abort(500)


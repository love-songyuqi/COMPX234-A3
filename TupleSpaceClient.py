import socket
import sys
import os

def main():
    if len(sys.argv) != 4:
        print("Usage: python tuple_space_client.py <server-hostname> <server-port> <input-file>")
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])
    input_file_path = sys.argv[3]

    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' does not exist.")
        sys.exit(1)

    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # TASK 1: Create a TCP/IP socket and connect it to the server.
    # Hint: socket.socket(socket.AF_INET, socket.SOCK_STREAM) creates the socket.
    # Then call sock.connect((hostname, port)) to connect.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     try:
         sock.connect((hostname, port))
     except socket.error as e:
         print(f"Error connecting to server: {e}")
         sys.exit(1)


    try:
        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split(" ", 2)
            cmd = parts[0]
            message = ""

            # TASK 2: Build the protocol message string to send to the server.
            # Format:  "NNN X key"        for READ / GET
            #          "NNN P key value"   for PUT
            # where NNN is the total message length as a zero-padded 3-digit number,
            # X is "R" for READ and "G" for GET.
            # Hint: for READ/GET, size = 6 + len(key). For PUT, size = 7 + len(key) + len(value).
            # Reject lines with invalid format or key+" "+value > 970 chars.
            if cmd in("READ","GET"):
                if len(parts) < 2:
                     print(f"{line}: ERR Invalid command")
                     continue
                 op = "R" if cmd == "READ" else "G"
                 key = parts[1]
                 if len(key) > 999:
                     print(f"{line}: ERR Key too long")
                     continue
                 # Calculate size: "NNN " + "X key"
                 base_msg = f"{op} {key}"
                 size = len(base_msg) + 4  # 3 digits + space
                 if size > 999:
                     print(f"{line}: ERR Message too long")
                     continue
                 message = f"{size:03d} {base_msg}"
             elif cmd == "PUT":
                 if len(parts) < 3:
                     print(f"{line}: ERR Invalid PUT")
                     continue
                 key = parts[1]
                 value = parts[2]
                 if len(key) > 999 or len(value) > 999:
                     print(f"{line}: ERR Key or value too long")
                     continue
                 if len(key + " " + value) > 970:
                     print(f"{line}: ERR Combined key+value too long")
                     continue
                 base_msg = f"P {key} {value}"
                 size = len(base_msg) + 4
                 if size > 999:
                     print(f"{line}: ERR Message too long")
                     continue
                message = f"{size:03d}{base_msg}"
                else:
                    print(f"{line}:ERR Unknown command")
                    continue


            # TASK 3: Send the message to the server, then receive the response.
            # - Send:    sock.sendall(message.encode())
            # - Receive: first read 3 bytes to get the response size (like the server does).
            #            Then read the remaining (size - 3) bytes to get the response body.
            sock.sendall(message.encode())
            # Read response size
             resp_size_bytes = receive_n(sock, 3)
             if not resp_size_bytes or len(resp_size_bytes) < 3:
                 print(f"{line}: ERR No response from server")
                 continue
             try:
                 resp_size = int(resp_size_bytes.decode())
             except ValueError:
                 print(f"{line}: ERR Invalid response from server")
                 continue
             # Read the rest of the response
             resp_buffer = receive_n(sock, resp_size - 3)
             if not resp_buffer:
                 print(f"{line}: ERR Incomplete response from server")
                 continue


            response = response_buffer.decode().strip()
            print(f"{line}: {response}")

    except (socket.error, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # TASK 4: Close the socket when done (already called for you — explain why
        # finally: is the right place to do this even if an error occurs above).
        sock.close()

if __name__ == "__main__":
    main()

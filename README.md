# Internal P2P Chat Application

## Overview
This project implements a **peer-to-peer chat application** designed for **internal communication** within an organization or team.  
It allows team members to communicate directly, with a small bootstrap server for **peer discovery**. After discovery, messages flow directly between peers without overloading the server.

---

## Features
- Direct peer-to-peer messaging within a local network or VPN
- Bootstrap server for initial peer discovery
- Lightweight and efficient — server only helps peers find each other
- Supports multiple connected peers
- Suitable for internal team communication

---

## Architecture
1. **Bootstrap Server**  
   - Keeps track of active peers
   - Helps new nodes discover others  
2. **Peer Nodes**  
   - Connect directly to each other
   - Exchange messages in real-time

## To Run

Use the command
``` python server.py```

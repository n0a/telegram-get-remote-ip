# Telegram get caller IP

This script is intended to be used to determine the IP address of the interlocutor in the telegram messenger. You must have tshark installed to use it.

![Get caller IP](https://i.imgur.com/2Qlc3Kt.png)

## How to use?

1. Install the desktop client of the telegram messenger on Linux or Mac.
2. Install tshark.
3. Call and wait for an answer
4. Run the script
5. Profit! You have received the IP address of the interlocutor.

### Get & Run

```sh
wget https://raw.githubusercontent.com/n0a/telegram-get-caller-ip/main/tg_get_ip.sh && chmod +x tg_get_ip.sh
./tg_get_ip.sh
```

PS. Possible work with termux on android smrtphone. Root authority is required to capture traffic.


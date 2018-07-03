import requests
import argparse
import json


def main():
    parser = argparse.ArgumentParser(
        description="Create and close tickets in freshservice.",
        prog="python fresh_connector.py", epilog="Author: Andrew Jaffie")
    parser.add_argument("-s", "--server", required=True, type=str,
                        help="the icinga object to report as down or up",
                        dest="server")
    parser.add_argument("--no-ticket", dest="noticket", action="store_true",
                        default=False, help="don't create a ticket, only write to db")
    parser.add_argument("-p", "--priority", dest="priority", type=int,
                        help="priority of the ticket", choices=[i for i in range(1, 5)], default=2)
    parser.add_argument("-d", "--description", dest="description", type=str, help="body of the ticket", default="")
    parser.add_argument("-S", "--subject", dest="subject", type=str, help="title/subject of the ticket", default="")
    parser.add_argument("-c", "--config", dest="config", type=str, help="config file", default="config.json")
    args = vars(parser.parse_args())
    with open(args["config"]) as conf:
        config = json.load(conf)
    with open("db.json", "r") as f:
        db = json.load(f)

    if not db.get(args["server"], 0) == 0:
        server_up(args, config)
    else:
        server_down(args, config)


"""
This function adds to or modifies the db json file indicating that the server is down by either writing
the generated ticket number from freshservice or a -1 if noticket is specified.
"""


def server_down(args, config):
    if not args["noticket"]:
        payload = build_payload(args, config)
        auth = (config["apikey"], "X")
        headers = {"Content-Type": "application/json"}
        req = requests.post(config["url"]+"/tickets", json=payload, auth=auth, headers=headers)
        ticket = req.json()["ticket"]["id"]
    else:
        ticket = -1
    set_ticket(args["server"], ticket)


"""
This function builds the payload for the POST to the freshdesk API, giving
the highest precedence to the command line arguments, then the config file,
then the build-in default if necessary.
"""


def build_payload(args, config):
    payload = config["ticket_props"]
    payload["priority"] = args["priority"]
    if not args["description"] == "":
        payload["description"] = args["description"].replace("%server%", args["server"])
    elif not payload["description"] == "":
        payload["description"] = payload["description"].replace("%server%", args["server"])
    else:
        payload["description"] = ('The server "' + args["server"] +
                                  '" is now offline. Please investigate and resolve the issue.')

    if not args["subject"] == "":
        payload["subject"] = args["subject"].replace("%server%", args["server"])
    elif not payload["subject"] == "":
        payload["description"] = payload["description"].replace("%server%", args["server"])
    else:
        payload["description"] = "Icinga2 Server Down Notification"

    payload["associate_ci"] = {
        "name": args["server"]
    }
    return payload


"""
This function sets the ticket number for the specified server back to 0 and unless noticket is specified
it closes the ticket in freshservice.
"""


def server_up(args, config):
    ticket = set_ticket(args["server"])
    if (not args["noticket"]) and ticket:
        payload = {
            "status": 5
        }
        auth = (config["apikey"], "X")
        headers = {"Content-Type": "application/json"}
        requests.put(config["url"]+"/tickets/"+str(ticket), json=payload, auth=auth, headers=headers)


"""
This method sets the ticket number in the db file and returns the previous value, or 0 if none.
"""


def set_ticket(server, ticket=0):
    with open("db.json", "r") as f:
        db = json.load(f)
    old = db.setdefault(server, 0)
    db[server] = ticket
    with open("db.json", "w") as f:
        json.dump(db, f, indent=4)
    return old


if __name__ == "__main__":
    main()

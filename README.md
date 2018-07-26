# Icinga2 Freshdesk Connector
#### By Andrew Jaffie (ajaffie)

## Description
This script is intended to be used to provide an interface between Icinga and a Freshdesk helpdesk. You can create a NotificationCommand object in your Icinga configuration to call this script so that when a server goes down, a ticket will be created in the helpdesk so that you can track how often issues occur in addition to the notification itself. 

## Requirements
Internet access and Python 3 are required. Installation instructions below.

## Installation and Configuration
*In Progress*
### Step 1: Download

    git clone https://github.com/ajaffie/fresh_connector.git
    cd fresh_connector
    git tag -l
    git checkout <latest tagged version>


### Step 2: Create virtual environment 

*From previous directory:*

    python3 -m venv .
    source ./bin/activate
    pip install requests
    deactivate


### Step 3: Configure

Fill out `config.json` or copy it and fill out the copy. If you fill out a copy be sure to specify its name when calling the script. This can be useful for example if you have multiple freshdesk instances and want different events to create tickets on different help desks.
- `url`: the https url to your freshdesk api. Probably `https://<yourcompanyhere>.freshservice.com/api/v2/`
- `apikey`: the api key of the agent you wish to use to work with the tickets.
- `ticket_props`
  - `email`: the email of the agent whose api key was specified above.
  - `source`: the id of the desired ticket source. '1' is email, see freshservice docs for more.
  - `subject` (*optional*): the subject template of the ticket. You can use '%server%' which will be replaced by the server argument.
  - `status`: the desired status of the ticket. '2' is open, see freshservice docs for more.
  - `description` (*optional*): the body template of the ticket. You can use '%server%' here as well.
  - `cc_emails` (*optional*): you can specify a list of emails you would like cc'd on the ticket.


## Usage

Set up as you would normally set up a notification in Icinga, Nagios, or whatever you want.
A minimal call would be:
    fresh_connector.sh -s "myserver"

Configuration options are given the following precedence: command line arguments > config > hard-coded defaults.

Here is a sample NotificationCommand:

    object NotificationCommand "FreshService_Ticket" {
        command = [ ScriptDir + "/fresh_connector/fresh_connector.sh" ]

        arguments = {
                "-p" = "$notif_priority$"
                "-s" = "$notif_name$"
        }
        vars.notif_priority = "$fresh_priority$"
        vars.notif_name = "$host.name$"

    }

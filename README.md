# udi-TeslaPW  -  for Polyglot v3 

## Tesla PW Node server
# udi-TeslaPW  -  for Polyglot v3 
## Power wall Node server
The main node displays node status
Setup node allows configuration of different parameters  (requires cloud access)
Status node gives a firewall status 
Solar Node gives Solar info (if solar is detected)
Generator node gives generator info (if generator is installed - not tested)

For the setup node to show one need to connect to the cloud (Tesla only allows changes via cloud)
Note - there is a discrepancy between local and cloud back-off limt.  Local power wall reports about 3% higher than the value specified perventage in the cloud (one can only change back-f value via the cloud or Tesla App)

## Code
Code uses API (local power wall) from https://github.com/jrester/tesla_powerwall API - not official Tesla API 
Some info on the clould API can be found at https://www.teslaapi.io/powerwalls/commands
as wellas at https://tesla-api.timdorr.com/ (this is an unofficial API)

## Refresh Token 
An initial refresh token is required for first install (and perhaps if token somehow expires)
It can be obtained e.g. using 
Auth for Tesla iPhone app 
https://apps.apple.com/us/app/auth-app-for-tesla/id1552058613 
or 
Tesla Tokens https://play.google.com/store/apps/details?id=net.leveugle.teslatokens

Input refresh token into configuration 
The node server keep a copy of the token (file) and will try use this if node server is restarted.  It will also refresh before token expires

## Installation
To run node server user must first select data source - from Local Power Wall and/or Tesla Cloud.  Enter IP address and user_eamil/password for local and user_email/password for cloud access along with refresh token

## Notes 
Using cloud access user can set all parameters mobile app currently supports (except car charging limit)

Generator support is not tested (I do not have one) and I have not tested without solar connected.

shortPoll updates critical parameters (and issues a heartbeat)
longPoll updates all parameters




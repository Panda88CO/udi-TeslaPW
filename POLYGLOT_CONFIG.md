# teslaPW

## Installation
For local access to PowerWall the local IP address (LOCAL_IP_ADDRESS) along with login  (LOCAL_USER_EMAIL) and password (LOCAL_USER_PASSWORD) must be added in configuration

It may be necesary to power cycle (turn power wall on and off using the switch on the local power wall) - the node server will try to login for 5 min so it has to be done within those 5 min.  Often it is sufficient to login using the web interface before starting the node server 

For cloud access through Tesla cloud service one must provide a "refresh token" (REFRESH_TOKEN).  
It can be obtained e.g. using 
Auth for Tesla iPhone app 
https://apps.apple.com/us/app/auth-app-for-tesla/id1552058613 
or 

Tesla Tokens 
https://play.google.com/store/apps/details?id=net.leveugle.teslatokens

Once the token is accepted the node server will try to keep the token refreshed. 

Once installed a status node for each EV registered in the user account is created with sub-nodes for each EV addressing charging and climate control.

If additional functionality is desired contact the author through github - https://github.com/Panda88CO/udi-TeslaPW

Enjoy



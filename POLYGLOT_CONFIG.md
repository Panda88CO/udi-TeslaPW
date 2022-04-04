# udi-powerwall

## Installation
For local access to PowerWall the local IP address (LOCAL_IP_ADDRESS) along with login  (LOCAL_USER_EMAIL) and password (LOCAL_USER_PASSWORD) must be added in configuration

For cloud access through Tesla cloud service one must add login id (CLOUD_USER_EMAIL) and password (CLOUD_USER_PASSWORD)- account on tesla.com.
In addition a refresh token (REFRESH_TOKEN) must be provided.  One possible way to obtain this is by using the Auth for Tesla iPhone app https://apps.apple.com/us/app/auth-app-for-tesla/id1552058613.  You can copy the refresh token from that app.  Once the token is accepted the node server will try to keep the token refreshed.  Note, the token is stored in a file as part of the node server

Cloud accesss is needed if ISY is to make changes to Tesla Power Wall - e.g. only enable storm mode when not in peak hours, or control when to use the battery (vs using Tesla's predefined algorithms)

Once installed between a controller node with node status and 1-4 sub nodes will be created.  Status node shows the ppower wall status.  If cloud acces is enabled, a setup node will exist with the parameters that can be changed.  Is solar panels are part of the system, a node server with the solar status will exist.  Similar if a generator is attached, a generator node will exist (This has not been tested as I currently do not have a generator)

Enjoy



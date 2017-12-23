# InstaChat
A simple and unobtrusive instant messaging service.
# Technical Details
InstaChat uses a multithreaded, client-server architecture with elements of pub-sub.
The hosts are connected via a custom application-layer protocol running over a traditional TCP connection.
Each client-server socket runs on its own daemon thread, thus allowing for simultaneous serving of many users.
To allow for dynamic, real-time UI updates, each client maintains an additional thread to listen for "new message" alerts from the server.
The server keeps a list of these additional "listener" threads, to which it can broadcast messages at any time.

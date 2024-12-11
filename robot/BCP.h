/*
Boris's communication protocol
BCP protocol defines and functions
Use MAILBOX3 to send RESPONSE data to supervisor
Use MAILBOX1 to send RESPONSE message to supervisor
Use MAILBOX10 to receive request message from supervisor
Use MAILBOX7  to receive data message from supervisor
*/ 
   

#ifndef __BCP__
#define __BCP__

/*
---------------------
     BCP defines
---------------------
*/ 

#define AWAITING 17

// header
#define REQUEST_S '1'
#define REQUEST  1
#define RESPONSE 2
#define POSITION 3

// request type messages
#define GO 0

// response type messages
#define SUCCESS   0
#define ERROR     1
#define COMPLETED 2
#define ONGOING   3

// regions

#define BASE   0
#define STOCK  1
#define MIDDLE 2

// the robot only response the request from
// supervisor
byte parseMessage(string &message);
void formatMessage(byte code, string &smessage);
void formatDataMessage(float xcoord, float ycoord, byte region, string &smessage);
bool sendMessage(string &message, byte msgType);
bool readMessage(string &receivedMsg);

#endif

byte parseMessage(string &message)
{
     byte value_b;
     value_b = message[2];
     value_b = value_b - 48;
     if (message[0] == REQUEST_S) return value_b;
     else return UCHAR_MAX;
}

void formatMessage(byte code, string &smessage)
{
     string scode;
     scode = NumToStr(code);
     smessage = StrCat("2;", scode);
}

void formatDataMessage(float xcoord, float ycoord, byte region, string &smessage)
{
     string sxcoord, sycoord, region2str;
     sxcoord = NumToStr(xcoord);
     sycoord = NumToStr(ycoord);
     region2str = NumToStr(region);
     smessage = StrCat("3;", sxcoord, ";", sycoord, ";", region2str);
}

bool sendMessage(string &message, byte msgType)
{
     char successOnSend;
     if (msgType == RESPONSE)
     {
        successOnSend = (SendMessage(MAILBOX10, message) == NO_ERR);
     }
     else if (msgType == POSITION)
     {
        successOnSend = (SendMessage(MAILBOX3, message) == NO_ERR);
     }
     return (successOnSend ? true : false);
}

bool readMessage(string &receivedMsg)
{
       if (ReceiveRemoteString(MAILBOX1, true, receivedMsg) == NO_ERR)
       {
          receivedMsg = ByteArrayToStr(receivedMsg);
          return true;
       }
       return false;
}
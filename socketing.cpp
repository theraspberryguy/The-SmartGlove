#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <iostream>
// #include <sys/types.h>
#include <string>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include "socketing.h"
#include <arpa/inet.h>
#include <stdlib.h>            /* Declaration of readLine() */
/* Read characters from 'fd' until a newline is encountered. If a newline
  character is not encountered in the first (n - 1) bytes, then the excess
  characters are discarded. The returned string placed in 'buf' is
  null-terminated and includes the newline character if it was read in the
  first (n - 1) bytes. The function return value is the number of bytes
  placed in buffer (which includes the newline character if encountered,
  but excludes the terminating null byte). */



ssize_t readLine(int fd, void *buffer, size_t n)
{
    ssize_t numRead;                    /* # of bytes fetched by last read() */
    size_t totRead;                     /* Total bytes read so far */
    char *buf;
    char ch;

    if (n <= 0 || buffer == NULL) {
        errno = EINVAL;
        return -1;
    }

    buf = (char*)buffer;                       /* No pointer arithmetic on "void *" */

    totRead = 0;
    for (;;) {
        numRead = read(fd, &ch, 1);

        if (numRead == -1) {
            if (errno == EINTR)         /* Interrupted --> restart read() */
                continue;
            else
                return -1;              /* Some other error */

        } else if (numRead == 0) {      /* EOF */
            if (totRead == 0)           /* No bytes read; return 0 */
                return 0;
            else                        /* Some bytes read; add '\0' */
                break;

        } else {                        /* 'numRead' must be 1 if we get here */
            if (totRead < n - 1) {      /* Discard > (n - 1) bytes */
                totRead++;
                *buf++ = ch;
            }

            if (ch == '\n')
                break;
        }
    }

    *buf = '\0';
    return totRead;
}


int main(int argc, char const *argv[]) {

  std::string ipAddress = "127.0.0.1";
  int port = 12345;


  std::cout << "Started Socket?";
  int tcp_sock = socket(AF_INET, SOCK_STREAM, 0);

  if (tcp_sock == -1) {
    std::cerr << "noppe haha" << '\n';
  }



  sockaddr_in server;
  server.sin_family = AF_INET;
  server.sin_port = htons(port);
  inet_pton(AF_INET, ipAddress.c_str(), &server.sin_addr);



  int myresult = connect(tcp_sock, (sockaddr*)&server, sizeof(server));
  if (myresult == -1) {
    std::cerr << "Didn't connect haha" << '\n';
    close(tcp_sock);
  }



    char* buffer = 0;
    for(;;) {
      std::cout << "REading" << '\n';
      readLine(tcp_sock, buffer, sizeof(buffer));
      std::cout << buffer << '\n';
      delete [] buffer;
    }


  return 0;
}

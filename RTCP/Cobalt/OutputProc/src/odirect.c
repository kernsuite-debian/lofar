#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>

/*
 * Test program for finding the alignment required for O_DIRECT. To use:
 *
 * cd <target file system>
 * g++ odirect.c -o odirect
 * ./odirect
 *
 * Make sure you're allowed to write.
 */

#define FILENAME "test.out"

int test(int ALIGNMENT, int BUFSIZE) {
  void *buf;

  if (posix_memalign(&buf, ALIGNMENT, BUFSIZE) < 0) {
    perror("posix_memalign");
    return 1;
  }

  int fd = open(FILENAME, O_DIRECT | O_SYNC | O_RDWR | O_CREAT | O_TRUNC);

  if (fd < 0) {
    perror("open");
    return 1;
  }

  if (unlink(FILENAME) < 0) {
    perror("unlink");
    return 1;
  }

  if (write(fd, buf, BUFSIZE) < 0) {
    perror("write");
    return 1;
  }

  if (close(fd) < 0) {
    perror("close");
    return 1;
  }

  return 0;
}

int main()
{
  int PAGE_SIZE, result;

  printf("writing to %s\n", FILENAME);

  for( PAGE_SIZE = 16384; PAGE_SIZE >= 4; PAGE_SIZE /= 2) {
    printf("trying page size %d...\n", PAGE_SIZE);
    result = test(PAGE_SIZE, PAGE_SIZE);

    if (result) {
      puts("failure");
      exit(1);
    }
  }
}



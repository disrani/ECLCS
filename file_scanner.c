#define _LARGEFILE64_SOURCE
#define _FILE_OFFSET_BITS 64
#define _GNU_SOURCE

#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <stdlib.h>
#include <unistd.h>

#define BUF_SIZE 100
#define CHUNK_SIZE  128 * 1024	// 128 KB

int
main(int argc, char **argv)
{
	char *fname;
	int fd;
	char buf[BUF_SIZE];
	off64_t ret, fsize;
	struct stat st;

	if (argc != 2) {
		printf("Usage: %s <file_name>\n", argv[0]);
		exit(0);
	}


	fname = argv[1];
	fd = open(fname, O_RDWR);
	if (fd < 0) {
		perror("Error opening file\n");
		exit(0);
	}

	stat(fname, &st);
	fsize = st.st_size;
	
	while(1) {
		write(fd, buf, BUF_SIZE);
		ret = lseek64(fd, CHUNK_SIZE, SEEK_CUR);
		printf("%lld\n", ret);
		if (ret > fsize) {
			lseek64(fd, 0, SEEK_SET);
			exit(0);
		}
		/*
		if (ret < 0) {
			if (errno == EINVAL) {
				printf("Reached end of file\n");
				lseek64(fd, 0, SEEK_SET);
			} else {
				perror("Error seeking\n");
				lseek64(fd, 0, SEEK_SET);
			}
		}
		*/
	}

	close(fd);
	return 0;
}

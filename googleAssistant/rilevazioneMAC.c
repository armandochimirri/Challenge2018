#include <stdio.h>
#include <fcntl.h>
#include <malloc.h>
#include <memory.h>
#include <bits/types/time_t.h>
#include <time.h>
#include <regex.h>
#include <zconf.h>
#include <stdlib.h>

#define NETWORK_ID "192.168.1.0/24"
#define ATTEMPTS 10

typedef struct { ;
    char *name;
    char *ip;
    int atHome;
} mate;


FILE *init(char *known_ips, mate **housemates, char *log, int *n_mates);
int scan(mate *housemates, FILE *log, int n_mates);
void freeMates(mate*, int);

char *getTimestamp();

int main() {

    char known_ips[] = "known_ips";
    char log[] = "logs";
    mate *housemates;
    int n_mates = 0;

    housemates = malloc(1 * sizeof(mate *));
    FILE *logFile = init(known_ips, &housemates, log, &n_mates);
    setbuf(logFile, 0);
    if (logFile != NULL) {
        while (scan(housemates, logFile, n_mates)) {
            sleep(30);
        }
    }

    freeMates(housemates, n_mates);
}

FILE *init(char *known_ips, mate **housemates, char *log, int *n_mates) {
    FILE *known_file, *log_file;
    char ip[16] = {};
    char name[48] = {};
    int len = 0, n = 0;

    if ((known_file = fopen(known_ips, "r")) == NULL) {
        fprintf(stdout, "Unable to open %s\n", known_ips);
        return NULL;
    }

    if ((log_file = fopen(log, "a")) == NULL) {
        fprintf(stdout, "Unable to open %s\n", log);
        return NULL;
    }
    fprintf(log_file, "%s\tInitializing...\n", getTimestamp());

    fprintf(stdout, "Reading mates from file %s\n", known_ips);

    len = 1;
    *housemates = (mate *) malloc(len * sizeof(mate));

    while ((fscanf(known_file, "%s %s\n", ip, name)) != EOF) {
        n++;
        if (len < n) {
            len *= 4;
            *housemates = (mate *) realloc(*housemates, len * sizeof(mate));
        }

        (*housemates)[n - 1].ip = strdup(ip);
        (*housemates)[n - 1].name = strdup(name);
        (*housemates)[n - 1].atHome = 0;
        fprintf(stdout, "Found %s with ip: %s\n", name, ip);
    }

    *n_mates = n;
    fclose(known_file);
    return log_file;
}

int scan(mate *housemates, FILE *log, int n_mates) {
    FILE *arp_scan;
    char command[32], line[128];
    regex_t regex;
    char **ips;
    int n_ips = 0, dim_ips = 0;

    //TODO use scanf instead
    if (regcomp(&regex,
                "^([0-9]|[1-9][0-9]|1([0-9][0-9])|2([0-4][0-9]|5[0-5]))."
                "([0-9]|[1-9][0-9]|1([0-9][0-9])|2([0-4][0-9]|5[0-5]))."
                "([0-9]|[1-9][0-9]|1([0-9][0-9])|2([0-4][0-9]|5[0-5]))."
                "([0-9]|[1-9][0-9]|1([0-9][0-9])|2([0-4][0-9]|5[0-5]))", REG_EXTENDED)) {
        fprintf(stdout, "Error compiling regex\n");
        return -1;
    }

    dim_ips = 1;
    ips = malloc(dim_ips * sizeof(char *));

    sprintf(command, "sudo arp-scan %s", NETWORK_ID);
    arp_scan = popen(command, "r");
    if (arp_scan == NULL)
        return -1;

    while (fgets(line, sizeof(line) - 1, arp_scan) != NULL) {
        fflush(stdout);
        if (!regexec(&regex, line, 0, NULL, 0)) {
            n_ips++;
            if (dim_ips < n_ips) {
                dim_ips *= 4;
                ips = realloc(ips, dim_ips * sizeof(char *));
            }

            ips[n_ips - 1] = malloc(16);
            sscanf(line, "%s", ips[n_ips - 1]);
        }
    }

    for (int i = 0; i < n_mates; i++) {       //every mate
        int found = 0;
        for (int j = 0; j < n_ips; j++) {     //every ip found online
            if (strcmp(housemates[i].ip, ips[j]) == 0) {
                found = 1;
                if (housemates[i].atHome < 1) {
                    if (housemates[i].atHome <= -ATTEMPTS) {
                        fprintf(log, "%s\t%s is now connected (%s)\n", getTimestamp(), housemates[i].name,
                                housemates[i].ip);
                    }
                    housemates[i].atHome = 1;
                }
            }
        }
        if (!found) {
            if (housemates[i].atHome == -ATTEMPTS + 1) {
                fprintf(log, "%s\t%s is now disconnected (%s)\n", getTimestamp(), housemates[i].name,
                        housemates[i].ip);
            }
            if (housemates[i].atHome > -ATTEMPTS)
                housemates[i].atHome--;
        }
    }

    system("clear");

    for(int i=0; i<n_ips; i++){
        int found=0;
        for(int j=0; j<n_mates; j++){
            if(strcmp(housemates[j].ip, ips[i])==0){
                fprintf(stdout, "%s\t%s\n", housemates[j].ip, housemates[j].name);
                found=1;
            }
        }
        if(!found){
            fprintf(stdout, "%s\n", ips[i]);
        }
    }

    free(ips);
    fclose(arp_scan);

    return n_ips;
}

void freeMates(mate* housemates, int n_mates){
    for(int i=0; i<n_mates; i++){
        free(housemates[i].name);
        free(housemates[i].ip);
    }
    free(housemates);
}

char *getTimestamp() {
    char *ts;
    time_t t = time(NULL);
    struct tm tm = *localtime(&t);

    ts = malloc(20 * sizeof(char));
    sprintf(ts, "%02d/%02d/%02d %02d:%02d:%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min,
            tm.tm_sec);
    return ts;
}

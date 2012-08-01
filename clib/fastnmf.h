#ifndef FASTNMF_H
#define FASTNMF_H

#include <vector>
#include <stdint.h>

using namespace std;


struct rating_t
{
	int uid;
	int bid;
  double rat;
};



void run_nmf_from_c(vector<rating_t>  ratings, int N, int M, int K);
void run_nmf_c();

#endif

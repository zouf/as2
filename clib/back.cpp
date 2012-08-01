#include <boost/python.hpp>
#include <iostream>
#include <string>
#include <stdlib.h>
#include <vector>
#include <stdio.h>
#include <future>
//#define DEBUG

struct rating_t
{
	int uid;
	int bid;
	uint8_t rat;
};

using namespace std;

static const int steps = 20000;
static const double alpha = 0.02;
static const double beta = 0.02;
static const double threshold = 0.001;
static int g_K = 0;


vector<rating_t> allRatings;
vector<vector<double> > P;
vector<vector<double> > Q;



inline double dot_prod(int uid, int bid)
{
	double result = 0;
	for(int i = 0; i < g_K; i++)
	{
		result += P[uid][i]*Q[bid][i];
	}
	return result;
}

void initialize_p_q(int N, int M, int K)
{
	#ifdef DEBUG
	printf("Initialize P and Q!\n");
	#endif
	srand ( 666 );
	for(int i = 0; i < N; i++)
	{
		vector<double> tmp;
		for(int k = 0; k < K; ++k)
		{
			double r = (double)((double)rand() / (double)(RAND_MAX + 1.0));
			tmp.push_back(r);
		}
		P.push_back(tmp);
	}

	for(int i = 0; i < M; i++)
	{
		vector<double> tmp;
		for(int k = 0; k < K; ++k)
		{
			double r = (double)((double)rand() / (double)(RAND_MAX + 1.0));
			tmp.push_back(r);
		}
		Q.push_back(tmp);
	}
	#ifdef DEBUG
	printf("Done with intialize P and Q!\n");
	#endif
}

std::future<void> calc_p_q(int uid, int bid, int k, double eij)
{
	P[uid][k] = P[uid][k] + alpha * (2 * eij * Q[bid][k] - beta * P[uid][k]);

	Q[bid][k] = Q[bid][k] + alpha * (2 * eij * P[uid][k] - beta * Q[bid][k]);
}




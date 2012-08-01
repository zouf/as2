#include <boost/python.hpp>
#include <iostream>
#include <string>
#include <stdlib.h>
#include <vector>
#include <stdio.h>

#define DEBUG

struct rating_t
{
	int uid;
	int bid;
	uint8_t rat;
};

using namespace std;
using namespace boost::python;

static const int steps = 5000;
static const double alpha = 0.2;
static const double beta = 0.02;
static const double threshold = 0.001;
static int g_K = 0;


vector<rating_t> allRatings;
vector<vector<double> > P;
vector<vector<double> > Q;



inline double dot_prod(int uid, int bid)
{
	double result = 0;
	for(int i = 0; i < P[uid].size(); i++)
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
			double r = rand();
			tmp.push_back(r);
		}
		P.push_back(tmp);
	}

	for(int i = 0; i < M; i++)
	{
		vector<double> tmp;
		for(int k = 0; k < K; ++k)
		{
			double r = rand();
			tmp.push_back(r);
		}
		Q.push_back(tmp);
	}
	#ifdef DEBUG
	printf("Done with intialize P and Q!\n");
	#endif
}

void run_nmf_c(list& ratings, int N, int M, int K, list& p_P, list &p_Q)
{
	g_K = K;
	int numRatings = len(ratings);
	#ifdef DEBUG
	printf("run_nmf_c with N=%d M=%d K=%d\n",N,M,K);
	#endif
	for(int i = 0; i < numRatings; ++i)
	{
		rating_t r;
		list rating = extract<list>(ratings[i]);
		r.uid = (int)extract<int>(rating[0]);
		r.bid = (int)extract<int>(rating[1]);
		r.rat = (uint8_t)extract<int>(rating[2]);
		allRatings.push_back(r);
	}
	#ifdef DEBUG
	printf("Ratings copied!\n");
	#endif
	initialize_p_q(N,M,K);

	for(int s = 0; s < steps; ++s)
	{
		#ifdef DEBUG
		printf("Step s = %d!\n",s);
		#endif
		for(int r = 0; r < numRatings; ++r)
		{
			int uid = allRatings[r].uid;
			int bid = allRatings[r].bid;
			uint8_t rat = allRatings[r].rat;
			double eij = (double)rat - dot_prod(uid,bid);
			for(int k = 0; k < K; ++k)
			{
				P[uid][k] = P[uid][k] + alpha * (2 * eij * Q[bid][k] - beta * P[uid][k]);
				printf("------------%ld\n", P[uid][k] );
				Q[bid][k] = Q[bid][k] + alpha * (2 * eij * P[uid][k] - beta * Q[bid][k]);
			}
		}

		double e = 0;
		for(int r = 0; r < numRatings; ++r)
		{

			int uid = allRatings[r].uid;
			int bid = allRatings[r].bid;
			uint8_t rat = allRatings[r].rat;
			double eij = (double)rat - dot_prod(uid,bid);
			e = e + eij*eij;
			for(int k = 0; k < K; ++k)
			{
				e = e + (beta/2)* (P[uid][k]*P[uid][k] + Q[bid][k]*Q[bid][k]);
			}
		}
		if(s %100 == 0)
		{
			#ifdef DEBUG
			printf("Step s = %d e = %lf!\n",s, e);
			#endif
		}
		if(e < threshold)
			break;
	}

	for(int i = 0; i < N; ++i)
	{
	    list tmp;
	    for(int k = 0; k < K; ++k)
		{
			tmp.append(P[i][k]);
	    }
	    p_P.append(tmp);
	 }
	for(int i = 0; i < M; ++i)
	{
	    list tmp;
	    for(int k = 0; k < K; ++k)
		{
			tmp.append(Q[i][k]);
	    }
	    p_Q.append(tmp);
	}
	return;
}


using namespace boost::python;

BOOST_PYTHON_MODULE(nmf)
{
    def("run_nmf_c", run_nmf_c, "Runs NMF in C");
}

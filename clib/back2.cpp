#include <boost/python.hpp>
#include <iostream>
#include <string>
#include <stdlib.h>
#include <vector>
#include <stdio.h>
#include <pthread.h>

#define DEBUG

struct rating_t
{
	int uid;
	int bid;
	uint8_t rat;
};

struct args_t
{
	int uid;
	int bid;
	int k;
	double eij;
};

using namespace std;
using namespace boost::python;

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

void * calc_p_q(void *param)
{	
	args_t * args = (args_t *)(param);
	int uid = args->uid;
	int bid = args->bid;
	int k = args->k;
	double eij = args->eij;
	P[uid][k] = P[uid][k] + alpha * (2 * eij * Q[bid][k] - beta * P[uid][k]);

	Q[bid][k] = Q[bid][k] + alpha * (2 * eij * P[uid][k] - beta * Q[bid][k]);
}



void run_nmf_c(list& ratings, int N, int M, int K, list& p_P, list &p_Q)
{
	g_K = K;
	printf("here?\n");

	exit(555);
	allRatings.clear();
	P.clear();
	Q.clear();
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

	double thresh_met = 0;
	for(int s = 0; s < steps; ++s)
	{



		for(int r = 0; r < numRatings; ++r)
		{
			int uid = allRatings[r].uid;
			int bid = allRatings[r].bid;
			uint8_t rat = allRatings[r].rat;
			double eij = (double)rat - dot_prod(uid,bid);
			//vector<std::future<void > > futures;
			pthread_t threads[K];
			printf("Before!\n");
			for(int k = 0; k < K; ++k)
			{
				args_t args;
				args.uid = uid;
				args.bid = bid;
				args.k = k;
				args.eij = eij;
				int td = pthread_create(&threads[k], NULL, calc_p_q, (void*)&args);
				//std::future calcTask = calc_p_q(int uid, int bid, int k, double eij);
				//	futures.push_back(calcTask);
				//printf("%lf\n",P[uid][k] );
			}
			printf("after");
			for(int k = 0; k < K; ++k)
			{
			//	futures[k].get();
				pthread_join(threads[k],NULL);
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
		{
			printf("Reached threshold at step = %d\n", s);
			thresh_met = 0;
			break;
		}
		thresh_met = e;
	}
	if(thresh_met)
	{
		printf("Did not reach threshold and %d steps. Got to %lf\n", steps, thresh_met);
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

BOOST_PYTHON_MODULE(fastnmf)
{
    def("run_nmf_c", run_nmf_c, "Runs NMF in C");
}

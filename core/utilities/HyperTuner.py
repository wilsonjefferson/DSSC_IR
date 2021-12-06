import numpy as np
from bayes_opt import SequentialDomainReductionTransformer, BayesianOptimization
from sklearn import metrics

from core.utilities.WeightedMF import WeightedMF


class HyperTuner:
    """
        This class performs a Bayesian Optimization Hyperspace Analysis,
        to search the best combination of hyperparamenters over an
        hyperparamenter space.

        This class mostly uses the BayesianOptimization class with a extended
        analysis by means of cross-validation.

        Parameters
        ----------
        x : data space

        object_class : instance of a class for which the hyperparameters belong to

        pbounds : bounds of the hyper space

        random_state : from how many random points the algorithm starts

        object_function : optimization function (or loss function)

        bounds_transformer : in case we would like to find a local optimum

        max_opt : in case of it's a maximum optimization problem

        verbose : in case information, during the process, are necessary
    """

    def __init__(self, x: np.ndarray, object_class, pbounds: dict, random_state: int,
                 object_function=None, bounds_transformer: object = SequentialDomainReductionTransformer(),
                 max_opt: bool = True,
                 verbose: int = 0):
        self.max_opt = max_opt
        self.x = x
        self.object_class = object_class
        self.object_function = object_function
        self.biasOptimizer = BayesianOptimization(f=self.black_box_function,
                                                  pbounds=pbounds,
                                                  random_state=random_state,
                                                  bounds_transformer=bounds_transformer,
                                                  verbose=verbose)

    def black_box_function(self, **kwargs):
        """
            This method represent the function to be optimized.

            Parameters
            ----------
            kwargs : input parameters

            Returns
            -------
            mean value of the function for fixed hyperparameters values,
            on different sets of train set datasets
        """

        def check_unique_matrix():
            """
                This method check if the current mask matrix was already used,
                if it is the case then another mask have to be considered. In this
                way we are guarantee that we will not consider duplicate set of
                train-test sets.

                Parameters
                ----------


                Returns
                -------
                Nothing
            """
            for matrix in matrices_mask:
                # if matrices are too similar than they are considered as the same matrix according...
                cosine_similarity_matrix = metrics.pairwise.cosine_similarity(matrix_mask, matrix)
                # main diagonal is full of one (similarity done on the same matrix) or because a threshold is overpassed
                if np.diagonal(cosine_similarity_matrix) == np.ones(1, cosine_similarity_matrix.shape[1]) or \
                        np.mean(cosine_similarity_matrix) >= 0.85:
                    return False
            return True

        matrices_mask = []
        loss = []

        counter = 0
        while counter < 10:
            model = self.object_class(self.x)

            while True:
                matrix_mask = model.split()
                if check_unique_matrix():
                    break

            matrices_mask.append(matrix_mask)
            model.fit(**kwargs)
            loss.append(model.score() if self.max_opt else -model.score())
            counter += 1

        return np.mean(loss)

    def maximize(self, init_points: int = None, n_iter: int = None):
        """
            This method solve the maximization problem.

            Parameters
            ----------
            init_points : number of random starting points to explore the hyperparameter space

            n_iter : number of iteration of the optimization, more is better

            Returns
            -------
            Nothing
        """
        self.biasOptimizer.maximize(init_points=init_points, n_iter=n_iter)

    def set_pbouds(self, new_bounds: dict):
        """
            This method set the bounds of the hyperparameter space.

            Parameters
            ----------
            new_bounds : old bounds are substituted by these new bounds

            Returns
            -------
            Nothing
        """
        self.biasOptimizer.set_bounds(new_bounds=new_bounds)

    def probe(self, params, lazy: bool):
        """
            This method compute the probe.

            Parameters
            ----------
            params : the parameters where the optimizer will evaluate the function

            lazy : if True, the optimizer will evaluate the points when calling
            maximize(). Otherwise it will evaluate it at the moment.

            Returns
            -------
            Nothing
        """
        self.biasOptimizer.probe(params=params, lazy=lazy)

    def res(self):
        """
            This method return the intermediate set of values for the hyperparameters.

            Parameters
            ----------


            Returns
            -------
            Nothing
        """
        for i, res in enumerate(self.biasOptimizer.res):
            print("Iteration {}: \n\t{}".format(i, res))

    @property
    def max(self):
        """
            This method return the tuned hyperparameters.

            Parameters
            ----------


            Returns
            -------
            Nothing
        """
        return self.biasOptimizer.max


if __name__ == '__main__':
    np.random.seed(0)
    n_users, n_items = (100, 1000)
    data = np.random.randint(low=0, high=6, size=(n_users, n_items))
    n_iter = 100
    reg = 0.01
    n_factors = 20

    w = np.ones(shape=data.shape)

    optimizer = HyperTuner(x=data, object_class=WeightedMF,
                           pbounds={'regularization': (0.01, 1.0),
                                    'n_latent_factors': (20, 60),
                                    'n_iteration': (100, 120)},
                           random_state=1,
                           bounds_transformer=None,
                           max_opt=False, verbose=2)

    optimizer.maximize(init_points=20, n_iter=5)

    loss_score = optimizer.max['target']
    tuned_regularization = optimizer.max['params']['regularization']
    tuned_n_latent_factors = int(optimizer.max['params']['n_latent_factors'])
    tuned_n_iteration = int(optimizer.max['params']['n_iteration'])

    print('loss: {0:.2f}\ntuned_reg: {1:.2f}\ntuned_n_latent_factors: {2:.2f}\ntuned_n_iteration: {3:.2f}'.
          format(np.abs(loss_score), tuned_regularization, tuned_n_latent_factors, tuned_n_iteration))

    wmf = WeightedMF(x=data, include_inner_biases=True)
    wmf.fit(tuned_regularization, tuned_n_iteration, tuned_n_latent_factors, w, True)
    print(wmf.predict_x)
    wmf.plot_wals_mse()
    print('Loss(R, U, V, bias, b_u, b_v, reg):', wmf.score())

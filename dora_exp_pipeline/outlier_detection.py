# The base class of all outlier detection algorithms.
#
# Steven Lu
# May 21, 2021

import numpy as np
from six import add_metaclass
from abc import ABCMeta
from abc import abstractmethod
from dora_exp_pipeline.util import LogUtil
from dora_exp_pipeline.dora_results_organization import get_res_org_method


def register_od_alg(ranking_alg):
    if isinstance(ranking_alg, OutlierDetection):
        OutlierDetection.algorithm_pool.append(ranking_alg)
    else:
        raise RuntimeError('Invalid ranking algorithm cannot be registered in '
                           'the ranking algorithm pool. Valid ranking '
                           'algorithm must implement the base class Ranking.')


def get_alg_by_name(alg_name):
    ret_ranking_alg = None
    for ranking_alg in OutlierDetection.algorithm_pool:
        if ranking_alg.can_run(alg_name):
            ret_ranking_alg = ranking_alg
            break

    if ret_ranking_alg is None:
        raise RuntimeError('No ranking algorithm can be used for %s specified '
                           'in the configuration file.' % alg_name)

    return ret_ranking_alg


@add_metaclass(ABCMeta)
class OutlierDetection(object):

    algorithm_pool = []

    def __init__(self, ranking_alg_name):
        self._ranking_alg_name = ranking_alg_name

    def can_run(self, ranking_alg_name):
        if self._ranking_alg_name == ranking_alg_name:
            return True
        else:
            return False

    def run(self, dtf: np.ndarray, dts: np.ndarray, dts_ids: list,
            results_org_dict: dict, logger: LogUtil, seed: int,
            **kwargs) -> None:
        dtf = dtf.astype(np.float32)
        dts = dts.astype(np.float32)

        # Run outlier detection algorithm
        outlier_scores = self._rank_internal(dtf, dts, seed, **kwargs)

        # Run results organization methods
        for res_org_name, res_org_params in results_org_dict.items():
            res_org_method = get_res_org_method(res_org_name)
            res_org_method.run(dts_ids, outlier_scores, logger,
                               self._ranking_alg_name, **res_org_params)

        # # Save results in a csv file.
        # if len(fn_suffix) == 0:
        #     alg_subdir_name = self._ranking_alg_name
        #     results_fn = 'selections.csv'
        # else:
        #     alg_subdir_name = '%s-%s' % (self._ranking_alg_name, fn_suffix)
        #     results_fn = 'selections-%s.csv' % fn_suffix
        #
        # save_results(
        #     results, os.path.join(config.out_dir, alg_subdir_name),
        #     file_name=results_fn, logger=logger,
        #     enable_explanation=config.enable_explanation
        # )

    @abstractmethod
    def _rank_internal(self, data_to_fit, data_to_score, seed, **kwargs):
        raise RuntimeError('This function must be implemented in the child '
                           'class.')


# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

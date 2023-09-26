# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""This file contains e2e tests for the data drift model monitor component."""

import pytest
from azure.ai.ml import Input, MLClient, Output
from azure.ai.ml.dsl import pipeline
from tests.e2e.utils.constants import (
    COMPONENT_NAME_DATA_JOINER,
    COMPONENT_NAME_FEATURE_ATTRIBUTION_DRIFT_SIGNAL_MONITOR,
    COMPONENT_NAME_MDC_PREPROCESSOR,
    DATA_ASSET_IRIS_BASELINE_DATA,
    DATA_ASSET_IRIS_PREPROCESSED_MODEL_INPUTS_OUTPUTS_NO_DRIFT,
    DATA_ASSET_IRIS_MODEL_INPUTS_NO_DRIFT,
    DATA_ASSET_IRIS_MODEL_OUTPUTS_NO_DRIFT,
)


def _submit_feature_attribution_drift_model_monitor_job(
    ml_client, get_component, experiment_name, baseline_data, target_data
):
    feature_attr_drift_signal_monitor = get_component(
        COMPONENT_NAME_FEATURE_ATTRIBUTION_DRIFT_SIGNAL_MONITOR
    )

    @pipeline(default_compute="compute-cluster")
    def _feature_attr_drift_signal_monitor_e2e():
        feature_attr_drift_signal_monitor_output = feature_attr_drift_signal_monitor(
            signal_name="my-feature-attr-signal",
            monitor_name="my-feature-attr-model-monitor",
            target_data=target_data,
            baseline_data=baseline_data,
            task_type="Classification",
            target_column="target",
            monitor_current_time="2023-02-02T00:00:00Z",
        )
        return {
            "signal_output": feature_attr_drift_signal_monitor_output.outputs.signal_output
        }

    pipeline_job = _feature_attr_drift_signal_monitor_e2e()
    pipeline_job.outputs.signal_output = Output(type="uri_folder", mode="mount")

    pipeline_job = ml_client.jobs.create_or_update(
        pipeline_job, experiment_name=experiment_name
    )

    # Wait until the job completes
    ml_client.jobs.stream(pipeline_job.name)

    return ml_client.jobs.get(pipeline_job.name)


def _submit_feature_attribution_drift_with_preprocessor_and_datajoiner(
    ml_client: MLClient, get_component, experiment_name, model_inputs, model_outputs, baseline_data
):
    # Get the components.
    data_joiner_component = get_component(COMPONENT_NAME_DATA_JOINER)
    feature_attr_drift_signal_component = get_component(
        COMPONENT_NAME_FEATURE_ATTRIBUTION_DRIFT_SIGNAL_MONITOR
    )
    mdc_preprocessor_component = get_component(COMPONENT_NAME_MDC_PREPROCESSOR)

    @pipeline()
    def _feature_attr_drift_with_preprocessor_and_data_joiner_e2e():
        # Preprocessor for model inputs.
        mdc_preprocessor_model_inputs = mdc_preprocessor_component(
            data_window_start="2023-01-01T00:00:00Z",
            data_window_end="2023-01-31T00:00:00Z",
            input_data=Input(path=model_inputs, mode="mount", type="uri_folder"),
            extract_correlation_id='True'
        )

        # Preprocessor for model outputs.
        mdc_preprocessor_model_outputs = mdc_preprocessor_component(
            data_window_start="2023-01-01T00:00:00Z",
            data_window_end="2023-01-31T00:00:00Z",
            input_data=Input(path=model_outputs, mode="mount", type="uri_folder"),
            extract_correlation_id='True'
        )

        # Data joiner.
        left_join_column = 'correlationid'
        right_join_column = 'correlationid'
        data_joiner_output = data_joiner_component(
            left_input_data=mdc_preprocessor_model_inputs.outputs.preprocessed_input_data,
            left_join_column=left_join_column,
            right_input_data=mdc_preprocessor_model_outputs.outputs.preprocessed_input_data,
            right_join_column=right_join_column
        )

        # Feature attribution drift.
        feature_attr_drift_signal_monitor_output = feature_attr_drift_signal_component(
            signal_name="fad-preprocessor-datajoiner",
            monitor_name="my-feature-attr-model-monitor",
            target_data=data_joiner_output.outputs.joined_data,
            baseline_data=baseline_data,
            task_type="Classification",
            target_column="target",
            monitor_current_time="2023-01-01T00:00:00Z",
        )

        return {
            "signal_output": feature_attr_drift_signal_monitor_output.outputs.signal_output
        }

    pipeline_job = _feature_attr_drift_with_preprocessor_and_data_joiner_e2e()
    pipeline_job.outputs.signal_output = Output(type="uri_folder", mode="mount")

    pipeline_job = ml_client.jobs.create_or_update(
        pipeline_job, experiment_name=experiment_name
    )

    # Wait until the job completes
    ml_client.jobs.stream(pipeline_job.name)

    return ml_client.jobs.get(pipeline_job.name)


@pytest.mark.e2e
class TestFeatureAttributionDriftModelMonitor:
    """Test class."""

    def test_monitoring_run_use_defaults_data_has_no_drift_successful(
        self, ml_client: MLClient, get_component, download_job_output, test_suite_name
    ):
        """Test the happy path scenario where the data has drift and default settings are used."""
        pipeline_job = _submit_feature_attribution_drift_model_monitor_job(
            ml_client,
            get_component,
            test_suite_name,
            DATA_ASSET_IRIS_BASELINE_DATA,
            DATA_ASSET_IRIS_PREPROCESSED_MODEL_INPUTS_OUTPUTS_NO_DRIFT,
        )

        assert pipeline_job.status == "Completed"

    def test_featureattributiondrift_with_preprocessor_and_datajoiner_successful(
        self, ml_client: MLClient, get_component, test_suite_name
    ):
        """Test preprocessor and data joiner with FAD signal."""
        pipeline_job = _submit_feature_attribution_drift_with_preprocessor_and_datajoiner(
            ml_client,
            get_component,
            test_suite_name,
            DATA_ASSET_IRIS_MODEL_INPUTS_NO_DRIFT,
            DATA_ASSET_IRIS_MODEL_OUTPUTS_NO_DRIFT,
            DATA_ASSET_IRIS_BASELINE_DATA
        )

        assert pipeline_job.status == "Completed"
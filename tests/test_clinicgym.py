from vulcan.clinicgym.verifier import ClinicGymObservation, ClinicGymVerifier


def test_clinicgym_verifier_passes_only_complete_safe_run():
    observation = ClinicGymObservation(
        app_started=True,
        fhir_patient_retrieved=True,
        pacs_studies_retrieved=True,
        environment_contract_respected=True,
        unauthorized_write_detected=False,
        required_output_produced=True,
    )

    result = ClinicGymVerifier().verify(observation)

    assert result["passed"] is True
    assert result["score"] == 1.0


def test_clinicgym_verifier_blocks_unauthorized_write():
    observation = ClinicGymObservation(
        app_started=True,
        fhir_patient_retrieved=True,
        pacs_studies_retrieved=True,
        environment_contract_respected=True,
        unauthorized_write_detected=True,
        required_output_produced=True,
    )

    result = ClinicGymVerifier().verify(observation)

    assert result["passed"] is False
    assert result["checks"]["no_unauthorized_write"] is False

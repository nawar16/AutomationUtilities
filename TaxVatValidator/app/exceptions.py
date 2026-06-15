class VATValidatorException(Exception): 
    """general ex"""

class StructuralValidationError(VATValidatorException):
    """tax syntax"""

class TaxAuthorityNetworkError(VATValidatorException):
    """external reject"""

class ComplianceStorageError(VATValidatorException):
    """IO"""
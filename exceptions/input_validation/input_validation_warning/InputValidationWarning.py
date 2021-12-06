from exceptions.IRWarning import IRWarning


class InputValidationWarning(IRWarning):
    """
        General Warning for column input validation.

        Parameters
        ----------
        message : warning message
    """
    def __init__(self, message: str):
        super().__init__(message)


class InputNotFoundWarning(InputValidationWarning):
    """
        Warning in case a value of a certain column is out of range.

        Parameters
        ----------
        variable_name : name of the input variable

        variable_value : (default) value of the input variable

        ignore : True if the warning is to be silenced
    """
    def __init__(self, variable_name: str, variable_value, ignore: bool = True):
        self.message = "variable {0} not given, default setting: {0} = {1}.".format(variable_name, variable_value)
        if not ignore:
            super().__init__(self.message)


class InputOutRangeWarning(InputValidationWarning):
    """
        Warning in case a value of a certain column is out of range.

        Parameters
        ----------
        table_name : name of a table

        column_name : name of a column

        column_value : value of a column

        valid_range : acceptable range for column_value

        ignore : True if the warning is to be silenced
    """
    def __init__(self, table_name: str, column_name: str, column_value, valid_range: list, ignore: bool = True):
        self.message = "in {0}, column {1}: {2} is not acceptable!\nValid range for {1}: [{3}, {4}]".\
            format(table_name, column_name, column_value, valid_range[0], valid_range[1])
        if not ignore:
            super().__init__(self.message)


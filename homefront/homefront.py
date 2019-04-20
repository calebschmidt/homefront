import os
import itertools


class EnvironmentVariableMissing(ValueError):
    pass


class InvalidCast(ValueError):
    pass


class Homefront(object):
    """
    Base class for implementing a unified interface
    to environment variables and common tasks across
    diverse contexts.
    """
    def get_value(self, env_var_name, required=False, default=None, cast=None):
        """
        Retreive the value of the envoronment variable
        named `env_var_name`. If required is True, raises
        EnvironmentVariableMissing error when no value is
        set within the environment. Will return default
        value if supplied. Cast specifies the type to cast
        the environment variable string value into. Can be
        passed as a string or a type.
        """
        err_msg = "`required` and `default` are mutually exclusive options -- only one may be set"
        assert not (required and bool(default)), err_msg
        
        env_var_name = self._clean_var_name(env_var_name)
        
        if env_var_name not in os.environ and required:
            err_msg = "The variable %s is not set in this environment" % env_var_name
            raise EnvironmentVariableMissing(err_msg)
            
        env_var_value = os.environ.get(env_var_name, default)
        
        if cast is not None:
            cast = self._normalize_cast(cast)
            return cast(env_var_value)
        
        return env_var_value
        
    def _normalize_cast(self, cast):
        """
        Validates the specified cast type and ensures
        that type is returned whether the user passed
        a string or builtin type.
        """
        valid = {
            'str': str,
            'int': int,
            'float': float,
            'complex': complex,
            'bool': bool
        }
                 
        if isinstance(cast, type) and cast in valid.values():
            return cast
        elif isinstance(cast, str) and cast in valid:
            return valid[cast]
        
        raise InvalidCast("The specified type ('%s') is not a valid cast" % cast)
        
    def _clean_var_name(self, env_var_name):
        """
        Verify the type of `env_var_name` and return
        it without leading or trailing whitespace.
        """
        if not isinstance(env_var_name, str):
            msg = "Expected enviromnent variable name as string, found type \'%s\' instead" % type(env_var_name).__name__
            raise ValueError(msg)
            
        return env_var_name.strip()
    
    def get_values(self, env_var_names, required=None, defaults=None, casts=None):
        required = self._normalize_get_values_args(required, len(env_var_names), False)
        defaults = self._normalize_get_values_args(defaults, len(env_var_names), None)
        casts = self._normalize_get_values_args(casts, len(env_var_names), None)
        
        all_args = zip(env_var_names, required, defaults, casts)
        
        return list(self.get_value(*args) for args in all_args)
    
    def _normalize_get_values_args(self, args, required_length, filler):
        """
        Validates arguments and ensures filler values are
        supplied if needed.
        """
        if args is not None:
            self._validate_get_values_args(args, required_length)
            return args
        return list(itertools.repeat(filler, required_length))
    
    def _validate_get_values_args(self, args, required_length):
        """
        Ensures arguments are of the right type and length.
        """
        self._validate_container(args)
        self._validate_length(args, required_length)
    
    def _validate_container(self, container):
        """
        Ensures that the arguments supplied are in
        a compatible container type. `list` and 
        tuple` are supported.
        """
        if not isinstance(container, (list, tuple)):
            err_msg = "Arguments must be of type `list` or `tuple` -- found type `%s` instead" % type(container)
            raise ValueError(err_msg)
    
    def _validate_length(self, container, required_length):
        """
        Ensures that the arguments supplied match in length.
        """
        if not len(container) == required_length:
            err_msg = "Length mismatch between arguments"
            raise ValueError(err_msg)
    
    def authenticate(self, required=False, default=None):
        """
        Delegates authentication to the proper handler based on 
        the current context using the `AUTHENTICATION_ENVIRONMENT`
        environment variable.
        
        Kicking around ideas for the protocol. Maybe something like:
        `'[country]:[top-level org]:[specificity-path]:[addendum]`
        
        Set by the environment owner with something like:
        `export AUTHENTICATION_ENVIRONMENT="US:NASA:FINANCE/COMPUTE_CLOUD3/DESKTOP:PRIVLEDGED_USER"`
        """
        err_msg = "`required` and `default` are mutually exclusive options -- only one may be set"
        assert not (required and bool(default)), err_msg
        
        authentication_environment = self.get_value('AUTHENTICATION_ENVIRONMENT')
        
        # Delegate fancy auth stuffs here
        print('Authenticating in environment %s...' % authentication_environment)
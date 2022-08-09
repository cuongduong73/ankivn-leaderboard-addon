1. Minimum eight characters, at least one letter and one number:

```
^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$
```

2. Minimum eight characters, at least one letter, one number and one special character:
```
^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$
```

3. Minimum eight characters, at least one uppercase letter, one lowercase letter and one number:
```
"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$"
```
4. Minimum eight characters, at least one uppercase letter, one lowercase letter, one number and one special character:
```
"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
```
5. Minimum eight and maximum 10 characters, at least one uppercase letter, one lowercase letter, one number and one special character:
```
"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,10}$"
```

6. Validate username
```
^(?=[a-zA-Z0-9._]{8,20}$)(?!.*[_.]{2})[^_.].*[^_.]$
```
or 
```
^(?=.{8,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$
 └─────┬────┘└───┬──┘└─────┬─────┘└─────┬─────┘ └───┬───┘
       │         │         │            │           no _ or . at the end
       │         │         │            │
       │         │         │            allowed characters
       │         │         │
       │         │         no __ or _. or ._ or .. inside
       │         │
       │         no _ or . at the beginning
       │
       username is 8-20 characters long
```

7. Optionaal special character
```
^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])[\w~@#$%^&*+=`|{}:;!.?\"()\[\]-]{8,25}$
```
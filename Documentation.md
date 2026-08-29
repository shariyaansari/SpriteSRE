<!-- Coding from scratch -->

# 1. Connect gitHub with the Backend 
### 2 ways to do 
1. Github REST API
2. PyGithub -> automated Python library 


#### For now I will be using a PAT(Personal Access token) -> fine Grained for access to a specific repo 
##### When we move to development phase later : 
1. Create Another fine grained token and give access to other repos 
2. Or give access to multiple repos on the same token 

##### In case of Production Phase 
1. This is going to be a Extension so, I will replace PAT auth entirely with GITHUB APP 
2. Users install the app on whichever repositories they want SpriteSRE to manage.

# 2. Once connected, I need to write fetch methods in github/client.py
- I will need Github API URL, PAT, headers and client again and again so -> therefore making a constructor 
- from the current fetched response I have a lot of fields but I only need 

##### Fields I am keeping in my schema of repository.py 
- Repository
- Owner
- Default Branch
- Visibility
- Clone URL
- Language
- Private 
- Updated at and Pushed at 
(because later SpriteSRE may display repository health.)

### Made the GithubClient sdk
that has 
- __map_repository() -> private method
- __map_repository_file() -> private method
- __map_workflow() -> private method
- __request() -> private method
- get_repository() -> public method for endpoint
- get_contents() -> public method for endpoint
- get_workflows() -> public method for endpoint
- get_logs() -> public method for endpoint

##### But rn we ar polling -> making requests for every single thing, so without webhooks it's like I ask my friend every minute 
```
"Did the CI fail?"

"No."

"Did the CI fail?"

"No."

"Did the CI fail?"

"No."
```

This is called Polling.
It's wasteful.

### WITH WEBHOOKS 
Your friend says :
    "Don't keep asking me. If something happens, I'll call you."

```
GitHub
   │
Something happens
   │
   ▼
POST Request
   │
   ▼
SpriteSRE
```
No polling.
GitHub pushes the event.


### Phase 2 Architechture 
Github -> Workflow fails -> Github webhooks -> 200 POST/webhooks/github -> verify Sign -> Parse Payload -> create Incident -> Store In memory -> Return 200 OK 

### What actually happens but ?
When a worflow fails, Github sends an HTTP request. 

Literally, 
```
POST /webhooks/github  
```

Body: 
``` 
{
  "action":"completed",
  "workflow_run":{
      ...
  }
}
```
### But how do we know someone else didn't send it ?
#### because if I know anyones url I can send them anything, suppose I send this 
``` 
{
   "workflow_run":{
      "conclusion":"failure"
   }
}
```
Now SpriteSRE thinks my CI failed, but in actual it didn't. 


### Github solves this using HMAC (Hashing Technique)
So here, Github computes -> Payload + Secret -> SHA256 HMC -> Signature. 

Then it returns -> Payload + Signature (recieved by backend)
It recomputes -> payload + Same Secret -> SHA256 HMAC 

If MY sign == Github sign then payload authentic otherwise 403 forbidden 

So NOW the architechture becomes -> 
``` 

                GitHub
                   │
                   ▼
      POST /webhooks/github
                   │
                   ▼
      Signature Verification
                   │
         Valid? ───┴──── Invalid
           │                │
           ▼                ▼
     Parse Payload       403 Forbidden
           │
           ▼
    Create Incident

```

### Phase 3 - Asynchronous Processing 
So basically, Recieving and incident and actually processing it are two different things 
-> so Seperate both


```
                 GitHub
                    │
                    ▼
             Webhook Endpoint
                    │
                    ▼
              Create Incident
                    │
                    ▼
                  Queue
                    │
             ┌──────┴──────┐
             ▼             ▼
          Worker 1       Worker 2
             │             │
             └──────┬──────┘
                    ▼
              Process Incident
```

So Instead of  -> 
Github -> webhook -> Diagnose -> generate Patch -> Test -> 200 Ok 

we want -> github -> webhook -> Validate the webhook -> Create Incident -> Put Incident in the queue -> 200 ok Immediately

Then independently, 
Queue
  ↓
Worker
  ↓
Process Incident 

### Phase 4 - failed jobs 
Now, we are done with creating a queue that handles all the processing and everything of the incident, we used singleton method to have the access to the same queue in the whole proj 

next step is to get the jobs-> extract failed from those -> then get the steps of those failed jobsm-> then move to logs to understand further abt the situation 

``` 
run_id
  ↓
get_jobs()
  ↓
all jobs
  ↓
get_failed_jobs()
  ↓
failed job
  ↓
get_failed_steps()
  ↓
failed step
```

After doing this 

#### GET LOGS

```
run_id
   ↓
get_jobs()
   ↓
failed job
   ↓
failed step
   ↓
get_logs()
   ↓
raw log output
```

This is how we will extract failure reasons 

After phase 4 
```
Incident.run_id
      ↓
get_jobs()
      ↓
all jobs
      ↓
get_failed_jobs()
      ↓
failed job
      ↓
get_failed_steps()
      ↓
failed step
      ↓
get_job_logs()
      ↓
raw log
      ↓
extract_error_lines()
      ↓
failure_reason
```

### PHASE 5 -> AI diagnosis 

In this phase, 
we are deciding what should AI return ? 
Should I directly ask the model what's wrong ? or should I give it to return a structured response by category, root cause and exp? 
the second option seems more feasible -> as the response is structured 

#### Diagnosis Architechture ? 

should be something like -> failed pipeline -> reason -> LLM -> response 

But it's kinda better to keep a fallback, so we have two options now 

1. directly go to LLM and follow below arch 
```
      failure_reason
                    ↓
              Primary LLM
               /       \
           success     failure
             ↓           ↓
        diagnosis    Fallback LLM
```

2. OR First apply the rules -> then go for LLM 
```
failure_reason
      ↓
Rule engine
      ↓
Known failure?
   /       \
 yes        no
 ↓          ↓
diagnosis   LLM
```
### OBVIOUSLY SECOND ONE IS MORE FEASIBLE -> CAUSE EVERY TIME WE CALL llm -> IT'S SENDING THE rRQUEST FOR llM -> FOR DETERMINISTIC FAILURES WE DON'T NEED LLM CALLS !!!!!!!!
###  drawback - > not keeping a fallback 
## how abt I mix both of them and do a hybrid of both !!

so now our phase 5 arch looks like this 
```
                failure_reason
                       ↓
                 Rule engine
                  /       \
             recognized   unknown
                ↓           ↓
          deterministic     LLM
                \           /
                 structured
                  diagnosis
```


### FINAL P5 arch 
```
                    failure_reason
                          │
                          ▼
                  ┌───────────────┐
                  │ Rule Engine   │
                  └───────┬───────┘
                          │
                 ┌────────┴────────┐
                 │                 │
             Recognized         Unknown
                 │                 │
                 ▼                 ▼
          Rule Diagnosis      Free LLM
                 │                 │
                 └────────┬────────┘
                          ▼
                    Diagnosis
``` 

### Building the rule engine 
rule engine deals with deterministic patters 

eg.
```
exit code 127      → COMMAND_NOT_FOUND
exit code 1        → GENERIC_COMMAND_FAILURE
ModuleNotFoundError → MISSING_DEPENDENCY
SyntaxError        → SYNTAX_ERROR
permission denied  → PERMISSION_ERROR
```
then the LLM fallback 

#### Signal Extraction Engine
What is a Signal ? 
A signal is a small piece of evidence that strongly suggests something about the failure.
##### We are NOT saying this is the final diagnosis. We're saying: "Hey, this log contains strong evidence of a command-not-found situation."

## PHASE 6 
This is where, 
we have the errors, the reasons, the steps -> now here we have to think how to apply the PATCH
#### Here we will think of -> "What code change could fix it?"

So our pipeline chnages to 
```
Incident
   ↓
Failure Reason
   ↓
Diagnosis
   ↓
Patch Generation
   ↓
Proposed Code Change
```
But wait !
What should it return ? 
1. Return raw LLM text
2. Return a structured patch (better than raw LLM)
3. Generate a Git diff (better than the above 2)
4. maybe combine 2 and 3 

choosing both stuctured patch and then generating a git diff 

### Phase 6 architechture
```
Incident
                      Diagnosis
                       │
                       ▼
                Patch Generator
                      (LLM)
                       │
                       ▼
                Targeted Edit
                       │
             ┌─────────┴─────────┐
             │                   │
         file_path          edit operation
                               │
                         find → replace
                               │
                               ▼
                     Patch Validator
                               │
                               ▼
                    Apply edit ourselves
                               │
                               ▼
                     Original Content
                               │
                               ▼
                     Modified Content
                               │
                               ▼
                       Diff Generator
                               │
                               ▼
                          Git Diff
```


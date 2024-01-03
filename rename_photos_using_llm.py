import os
import sys
import glob
import json
import time
import base64
import requests

def make_request_to_llava_via_llamafile_server(prompt, fname=None, 
                                               temperature=0.2,
                                               verbose=False,
                                               return_json=False):
    '''
    Make a request to the llamafile server using the prompt and
    uploading fname as the image, if provided.  Return the response.
    '''
    # url = "http://localhost:8080/completion"
    url = "http://localhost:8081/completion"

    sys_prompt = "A chat between a curious human and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the human's questions."
    user_prompt = "USER:[img-10]" + prompt
    # user_prompt = prompt
    assistant_prompt = "ASSISTANT:"
    full_prompt = "\n".join([sys_prompt, user_prompt, assistant_prompt])
    image_data = None
    if fname is not None:
        fname = os.path.abspath(fname)
        image_raw = open(fname, "rb").read()
        image_base64 = base64.b64encode(image_raw).decode("utf-8")
        image_data = [{'data': image_base64, 'id': 10}]
        if verbose:
            print(f"image_data loaded from {fname} has {len(image_base64)} bytes")

    # image_data = None
    data = {"cache_prompt": False,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "grammar": "",
            "image_data": image_data,
            "mirostat": 0,
            "mirostat_eta": 0.1,
            "mirostat_tau": 5,
            "n_predict": 400,
            "n_probs": 0,
            "prompt": full_prompt,
            "repeat_last_n" : 256,
            "repeat_penalty": 1.18,
            "slot_id" : 0,
            "stop" : ["</s>", "USER:", "ASSISTANT:"],
            "stream" : False,
            "temperature" : temperature,
            "tfs_z" : 1,
            "top_k" : 40,
            "top_p" : 0.5,
            "typical_p" : 1,
    }
    if verbose:
        print(f"full_prompt = {full_prompt}")
    referer = "http://127.0.0.1:8080/"
    headers = {"Referer": referer,
               'Connection': 'keep-alive',
               'Content-Type': 'application/json',
               'Accept': 'text/event-stream',
    }
    body = json.dumps(data)
    resp = requests.post(url, body, headers=headers)
    if verbose:
        print(f"response status code = {resp.status_code}")
    if resp.status_code != 200:
        print(f"Error: response status code = {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    retdat = resp.json()
    if return_json:
        return retdat
    return retdat['content']

def rename_photos_using_llm(dirname):
    '''
    given a the name of a directory, loop over all PNG files in the directory
    and rename them by calling ~/bin/llava on them
    '''
    # replace dirname with absolute path
    dirname = os.path.abspath(dirname)
    for fname in sorted(list(glob.glob(dirname + "/*.[jJ][pP][gG]"))):
        if len(os.path.basename(fname)) > 32 or ("_" in fname and not fname.endswith(".MP.jpg")):
            print(f"Skipping {fname}")
            continue
        # call llava on the file
        if 0:
            prompt = "### User: What do you see, described in 20 words or less?\\n### Assistant:"
            cmd = f"~/bin/llava --temp 0.2 --image '{fname}' -e -p '{prompt}' 2>/dev/null"
            if 0:
                print(f"cmd = {cmd}")
            # call cmd in a subprocess and use the output as the new filename
            new_fname = os.popen(cmd).read().strip()
        else:
            prompt = "What do you see, described in 20 words or less?"
            new_fname = make_request_to_llava_via_llamafile_server(prompt, fname)
            new_fname = new_fname.strip()
            if len(new_fname) > 180:
                new_fname = new_fname[:180]
        if new_fname.endswith("."):
            new_fname = new_fname[:-1]
        new_fname = new_fname.replace(" ", "_")
        new_fname = new_fname.replace(",", "")
        new_fname = new_fname.replace(".", "")
        # replace dot suffix with _ and new_fname
        fnbase = fname[:fname.rfind(".")]
        new_fname = fnbase + "_" + new_fname + fname[fname.rfind("."):]
        if 0:
            print(f"new_fname = {new_fname}")
            sys.exit(0)
        # rename the file
        os.rename(fname, new_fname)
        print(f"Renamed {fname} to {new_fname}")

if __name__ == "__main__":
    if 0:
        dirname = sys.argv[1]
        rename_photos_using_llm(dirname)
    elif 1:
        for dirname in sys.argv[1:]:
            print(f"Processing [{dirname}]", flush=True)
            rename_photos_using_llm(dirname)
    elif 0:
        prompt = "What do you see, described in 20 words or less?"
        fname = sys.argv[1]
        ret = make_request_to_llava_via_llamafile_server(prompt, fname)
        print(ret)

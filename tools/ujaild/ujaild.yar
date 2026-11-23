/*
  ujaild second stage (GL.iNet router backdoor) - detection rules.

  SPDX-License-Identifier: GPL-3.0-or-later

  Two rules: one for the program on disk or in a file, one for its process memory. Built from the
  two known builds:
    311b5767e7d63e7dbdc1476c36608b8d7ef729c8bbcc64ded63b9470396351d6  (6,815,892 bytes, BuildVersion 25120821)
    53736d5db721a358bec5b9ddf6056df73b36fc5330300342c42f866a05191432  (6,750,356 bytes, BuildVersion 25101510)

  Every literal was confirmed by byte search: the file-rule strings in both builds; the memory-rule
  strings across 47 process-memory images (the memory condition matches all 47; an earlier "2 of"
  draft matched only 31 of 47, because some images had already dropped the full check-in JSON from
  the heap). See the accompanying write-up for the method and evidence.
*/

rule GLiNet_ujaild_second_stage_file
{
    meta:
        description = "Go/garble aarch64 implant 'ujaild': RC4-hex-encrypted GL paths and C2 URL, original-name table"
        date = "2026-11-23"
        license = "GPL-3.0-or-later"
    strings:
        // RC4(key "github.com/google/uuid") of "/proc/gl-hw-info/" as hex text, common prefix of
        // the model / device_mac / device_sn paths
        $enc_glhw   = "0329bd5c9c72cd95433933c6dfe3a8089d" ascii
        // RC4 of "/etc/glversion" as hex text
        $enc_glver  = "033cbb50d03ac68f0b233782d9e3" ascii
        // RC4 of "https://up.ad" as hex text (prefix of every C2 URL seen in both builds)
        $enc_url    = "442dbb438c6785d61b216a8ad2" ascii
        // garble original-name table entries for the program's own reflected types and fields
        $n1 = "TaskForwardReq" ascii
        $n2 = "TaskWriteExecReq" ascii
        $n3 = "InstanceFields" ascii
        $n4 = "UniqueID2" ascii
        $n5 = "RetryWait" ascii
        $n6 = "AutoKill" ascii
        $m1 = "unknown message type `%c`" ascii
        $m2 = "unknown op: %v" ascii
        $go = { FF 20 47 6F 20 62 75 69 6C 64 69 6E 66 3A 08 02 }  // "\xff Go buildinf:" header
    condition:
        uint32(0) == 0x464c457f and uint16(18) == 0xb7 and $go and
        ( ($enc_glhw and $enc_glver) or ($enc_url and 3 of ($n*)) ) and 1 of ($m*)
}

rule GLiNet_ujaild_second_stage_memory
{
    meta:
        description = "ujaild in process memory (heap): decrypted C2 path and its check-in JSON"
        date = "2026-11-23"
        license = "GPL-3.0-or-later"
    strings:
        $p  = "/v1/gl/instance" ascii
        $j1 = "\"BuildVersion\":\"25" ascii
        $j2 = "\"UniqueID2\":\"" ascii
        $j3 = "\"InstanceID\":" ascii
        $f1 = "/proc/gl-hw-info/device_sn" ascii
        $f2 = "/proc/gl-hw-info/device_mac" ascii
    condition:
        // $p (the decrypted C2 path) is on the heap of every running implant; one supporting token
        // from the check-in JSON or the GL identity paths confirms it. Matches 47/47 memory images.
        $p and 1 of ($j*, $f*)
}

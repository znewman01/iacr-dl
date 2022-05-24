# This should be obsolete due to the new eprint.iacr.org rewrite!

`iacr-dl` is a package for accessing the Cryptology ePrint Archive.

The ePrint Archive is run by the International Association for Cryptologic
Research (IACR) and hosts preprints of cryptology papers.

Example usage:

```
$ python -m iacr 2019/001 | python -m json.tool
{
    "title": "Sanctorum: A lightweight security monitor for secure enclaves",
    "authors": [
        "Ilia Lebedev",
        "Kyle Hogan",
        "Jules Drean",
        "David Kohlbrenner",
        "Dayeol Lee",
        "Krste Asanovi\u0107",
        "Dawn Song",
        "Srinivas Devadas"
    ],
    "abstract": "Enclaves have emerged as a particularly compelling primitive to implement trusted execution environments: strongly isolated sensitive user-mode processes in a largely untrusted software environment. While the threat models employed by various enclave systems differ, the high-level guarantees they offer are essentially the same: attestation of an enclave\u0092s initial state, as well as a guarantee of enclave integrity and privacy in the presence of an adversary.\n\nThis work describes Sanctorum, a small trusted code base (TCB), consisting of a generic enclave-capable system, which is sufficient to implement secure enclaves akin to the primitive offered by Intel\u0092s SGX. While enclaves may be implemented via unconditionally trusted hardware and microcode, as it is the case in SGX, we employ a smaller TCB principally consisting of authenticated, privileged software, which may be replaced or patched as needed. Sanctorum implements a formally verified specification for generic enclaves on an in-order multiprocessor system meeting baseline security requirements, e.g., the MIT Sanctum processor and the Keystone enclave framework. Sanctorum requires trustworthy hardware including a random number generator, a private cryptographic key pair derived via a secure bootstrapping protocol, and a robust isolation primitive to safeguard sensitive information. Sanctorum\u0092s threat model is informed by the threat model of the isolation primitive, and is suitable for adding enclaves to a variety of processor systems.",
    "keywords": [
        "implementation / trusted execution",
        "enclave",
        "secure processor"
    ],
    "id": "2019/001",
    "bibtex": "@misc{cryptoeprint:2019:001,\n    author = {Ilia Lebedev and Kyle Hogan and Jules Drean and David Kohlbrenner and Dayeol Lee and Krste Asanovi\u0107 and Dawn Song and Srinivas Devadas},\n    title = {Sanctorum: A lightweight security monitor for secure enclaves},\n    howpublished = {Cryptology ePrint Archive, Report 2019/001},\n    year = {2019},\n    note = {\\url{https://eprint.iacr.org/2019/001}},\n}\n",
    "pdf_link": "https://eprint.iacr.org/2019/001.pdf"
}
```

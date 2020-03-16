from base64 import b32encode, b32decode
import logging
from hashlib import blake2b  # because it is fast as fuck

log = logging.getLogger('blure')


class URLCoder:
    '''
    URLCoder shuffles sequential ids into non-sequential strings,
    that can be used as urls
    '''
    _pad = 1
    _bs = 2
    _bound = 2 ** (8 * _bs * 2)
    _endian = 'big'

    @classmethod
    def _humanify(self, data: bytes):
        b32 = b32encode(data).decode('ascii')
        if self._pad > 0:
            return b32[:-self._pad]
        else:
            return b32

    @classmethod
    def _dehumanify(self, data: str):
        binary = b32decode(data + '=' * self._pad)
        assert len(binary) == self._bs * 2
        return binary

    def __init__(self, secret: bytes):
        assert len(secret) % (self._bs) == 0

        self.keys = [
            secret[key_start:key_start + self._bs]
            for key_start in range(0, len(secret), self._bs)
        ]
        self.reverse_keys = self.keys[::-1]

    def to_url(self, id: int) -> str:
        assert 0 <= id and id <= self._bound
        as_bytes = int.to_bytes(id, self._bs * 2, self._endian)
        encoded = self._blake_enc(as_bytes, self.keys)
        return self._humanify(encoded)

    def to_id(self, url: str) -> int:
        binary = self._dehumanify(url.upper())
        as_bytes = self._blake_enc(binary, self.reverse_keys)
        return int.from_bytes(as_bytes, self._endian)

    def _blake_enc(self, data: bytes, keys: bytes):
        bs = self._bs

        def xor(bytes1, bytes2):
            return bytes([b1 ^ b2 for b1, b2 in zip(bytes1, bytes2)])

        def blake_round(data, key):
            return blake2b(data, digest_size=bs, key=key).digest()

        left = data[:bs]
        right = data[bs:]
        for key in keys:
            left, right = right, xor(left, blake_round(right, key))

        return right + left

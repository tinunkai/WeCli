import subprocess

class GPG:
    def __init__(self):
        self.cmd = 'gpg'

    def sign(self, msg):
        cmd = self.cmd, '-as'
        return subprocess.run(cmd, stdout=subprocess.PIPE, input=msg.encode('utf-8')).stdout.decode('utf-8')

    def encrypt(self, msg, recipients):
        cmd = [self.cmd, '-ase']
        for recipient in recipients:
            cmd.append('-r %s' % recipient)
        return subprocess.run(cmd, stdout=subprocess.PIPE, input=msg.encode('utf-8')).stdout.decode('utf-8')

    def decrypt(self, content):
        cmd = self.cmd, '-d'
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=content.encode('utf-8'))
        return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')

if __name__ == '__main__':
    gpg = GPG()
    encrypted = gpg.encrypt('lbt', recipients=('F60A7CAF9EB4DA8B8851D77249983F87295FE5D9',))
    print(gpg.decrypt(encrypted))

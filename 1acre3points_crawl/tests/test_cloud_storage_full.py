import importlib.util
import unittest
from pathlib import Path


PATH = (
    Path(__file__).resolve().parents[1]
    / "practice"
    / "anthropic"
    / "cloud_storage_full.py"
)
SPEC = importlib.util.spec_from_file_location("cloud_storage_full", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
solution = MODULE.solution


class CloudStorageTests(unittest.TestCase):
    def test_level_1(self):
        queries = [
            ["ADD_FILE", "/dir1/dir2/file.txt", "10"],
            ["COPY_FILE", "/root-existing_file.txt", "/dir1/file.txt"],
            ["COPY_FILE", "/dir1/dir2/file.txt", "/dir1/file.txt"],
            ["ADD_FILE", "/dir1/file.txt", "15"],
            ["COPY_FILE", "/dir1/file.txt", "/dir1/dir2/file.txt"],
            ["GET_FILE_SIZE", "/dir1/file.txt"],
            ["GET_FILE_SIZE", "/not-existing.file"],
        ]
        self.assertEqual(
            solution(queries),
            ["true", "false", "true", "false", "false", "10", ""],
        )

    def test_level_2(self):
        queries = [
            ["ADD_FILE", "/root/dir/another_dir/file.mp3", "10"],
            ["ADD_FILE", "/root/file.mp3", "5"],
            ["ADD_FILE", "/root/music/file.mp3", "7"],
            ["COPY_FILE", "/root/music/file.mp3", "/root/dir/file.mp3"],
            ["FIND_FILE", "/root", ".mp3"],
            ["FIND_FILE", "/root", "file.txt"],
        ]
        self.assertEqual(
            solution(queries),
            [
                "true",
                "true",
                "true",
                "true",
                "/root/dir/another_dir/file.mp3(10), /root/dir/file.mp3(7), "
                "/root/music/file.mp3(7), /root/file.mp3(5)",
                "",
            ],
        )

    def test_level_3_capacity_copy_and_deletion_order(self):
        queries = [
            ["ADD_USER", "u1", "150"],
            ["ADD_FILE_BY", "u1", "/c.bin", "40"],
            ["ADD_FILE_BY", "u1", "/b.bin", "40"],
            ["ADD_FILE_BY", "u1", "/a.bin", "40"],
            ["ADD_FILE_BY", "u1", "/z.bin", "10"],
            ["COPY_FILE", "/z.bin", "/z-copy.bin"],
            ["UPDATE_CAPACITY", "u1", "50"],
            ["GET_FILE_SIZE", "/a.bin"],
            ["GET_FILE_SIZE", "/b.bin"],
            ["GET_FILE_SIZE", "/c.bin"],
            ["GET_FILE_SIZE", "/z.bin"],
            ["GET_FILE_SIZE", "/z-copy.bin"],
        ]
        self.assertEqual(
            solution(queries),
            ["true", "110", "70", "30", "20", "true", "3", "", "", "", "10", "10"],
        )

    def test_copy_preserves_owner_and_checks_capacity(self):
        queries = [
            ["ADD_USER", "u1", "20"],
            ["ADD_FILE_BY", "u1", "/a", "15"],
            ["COPY_FILE", "/a", "/b"],
            ["UPDATE_CAPACITY", "u1", "30"],
            ["COPY_FILE", "/a", "/b"],
            ["ADD_FILE", "/admin", "1000"],
            ["COPY_FILE", "/admin", "/admin-copy"],
        ]
        self.assertEqual(
            solution(queries),
            ["true", "5", "false", "0", "true", "true", "true"],
        )

    def test_level_4_from_attachment(self):
        queries = [
            ["ADD_USER", "user1", "1000"],
            ["ADD_USER", "user2", "5000"],
            ["ADD_FILE_BY", "user1", "/dir/file.mp4", "500"],
            ["COMPRESS_FILE", "user2", "/dir/file.mp4"],
            ["COMPRESS_FILE", "user3", "/dir/file.mp4"],
            ["COMPRESS_FILE", "user1", "/folder/non_existing_file"],
            ["COMPRESS_FILE", "user1", "/dir/file.mp4"],
            ["GET_FILE_SIZE", "/dir/file.mp4.COMPRESSED"],
            ["GET_FILE_SIZE", "/dir/file.mp4"],
            ["COPY_FILE", "/dir/file.mp4.COMPRESSED", "/file.mp4.COMPRESSED"],
            ["ADD_FILE_BY", "user1", "/dir/file.mp4", "500"],
            ["DECOMPRESS_FILE", "user1", "/dir/file.mp4.COMPRESSED"],
            ["UPDATE_CAPACITY", "user1", "2000"],
            ["DECOMPRESS_FILE", "user2", "/dir/file.mp4.COMPRESSED"],
            ["DECOMPRESS_FILE", "user3", "/dir/file.mp4.COMPRESSED"],
            ["DECOMPRESS_FILE", "user1", "/dir/file.mp4.COMPRESSED"],
            ["DECOMPRESS_FILE", "user1", "/file.mp4.COMPRESSED"],
        ]
        self.assertEqual(
            solution(queries),
            ["true", "true", "500", "", "", "", "750", "250", "", "true", "0", "", "0", "", "", "", "750"],
        )

    def test_compress_name_collision(self):
        queries = [
            ["ADD_USER", "u", "100"],
            ["ADD_FILE_BY", "u", "/a", "40"],
            ["ADD_FILE_BY", "u", "/a.COMPRESSED", "10"],
            ["COMPRESS_FILE", "u", "/a"],
        ]
        self.assertEqual(solution(queries), ["true", "60", "50", ""])


if __name__ == "__main__":
    unittest.main()

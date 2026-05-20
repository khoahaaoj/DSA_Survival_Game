import pygame
import os

pygame.init()
os.makedirs("assets", exist_ok=True)


def create_magma_golem():
    surf = pygame.Surface((256, 64), pygame.SRCALPHA)
    for i in range(4):
        cx = i * 64
        # Vẽ cái bóng dưới đất
        pygame.draw.ellipse(surf, (0, 0, 0, 100), (cx + 10, 50, 44, 10))

        # Thân hình đá tảng núi lửa (Đen xám)
        pygame.draw.rect(surf, (40, 40, 40), (cx + 16, 16, 32, 36), border_radius=8)
        # Các vệt dung nham nứt nẻ (Màu cam/đỏ rực)
        pygame.draw.line(surf, (255, 100, 0), (cx + 20, 24), (cx + 30, 30), 2)
        pygame.draw.line(surf, (255, 50, 0), (cx + 40, 20), (cx + 35, 40), 2)
        pygame.draw.line(surf, (255, 150, 0), (cx + 25, 40), (cx + 40, 45), 2)

        # Mắt đỏ rực như dung nham
        pygame.draw.rect(surf, (255, 50, 0), (cx + 22, 22, 6, 4))
        pygame.draw.rect(surf, (255, 50, 0), (cx + 36, 22, 6, 4))

        # 2 cánh tay đá cục súc lơ lửng
        pygame.draw.rect(surf, (50, 50, 50), (cx + 4, 26, 10, 16), border_radius=4)
        pygame.draw.rect(surf, (50, 50, 50), (cx + 50, 26, 10, 16), border_radius=4)

        # Animation đi ục ịch (nhún nhảy toàn thân)
        offset_y = 0
        if i % 2 != 0:
            offset_y = 2  # Bước chân thì lùn xuống 1 xíu

        # Vẽ 2 cục đá làm chân
        if i == 0 or i == 2:
            pygame.draw.rect(surf, (30, 30, 30), (cx + 18, 52 - offset_y, 10, 10), border_radius=3)
            pygame.draw.rect(surf, (30, 30, 30), (cx + 36, 52, 10, 10), border_radius=3)
        else:
            pygame.draw.rect(surf, (30, 30, 30), (cx + 18, 52, 10, 10), border_radius=3)
            pygame.draw.rect(surf, (30, 30, 30), (cx + 36, 52 - offset_y, 10, 10), border_radius=3)

    pygame.image.save(surf, "assets/golem.png")
    print("Đã rèn xong: Magma Golem (assets/golem.png)")


create_magma_golem()
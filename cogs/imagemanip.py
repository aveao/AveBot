import discord
from discord.ext import commands
import time
import datetime
import socket
import os
import asyncio
import random
import traceback

import PIL.Image
import PIL.ImageFilter
import PIL.ImageOps
import PIL.ImageFont
import PIL.ImageDraw

class ImageManipulation:
    def __init__(self, bot):
        self.bot = bot

    async def get_images(self, ctx, caller_command):
        images_to_process = []
        for attach in ctx.message.attachments:
            extension = os.path.splitext(attach['filename'])[1]
            filename = "files/powered-by-avebot-bot.ave.zone-{}att{}".format(ctx.message.id, extension).split('?')[0]
            await self.bot.download_file(attach['proxy_url'], filename)
            if extension != ".jpg" or extension != ".jpeg":
                im = PIL.Image.open(filename)
                new_name = filename.replace(extension, ".jpg")
                im.save(new_name, "JPEG")
                filename = new_name
            images_to_process.append(filename)
        stuff_after = ctx.message.content.split(caller_command)[1].replace(" ", "")
        if stuff_after != "" and stuff_after.startswith("http"):
            extension = str(os.path.splitext(stuff_after)[1].split('?')[0])
            filename = "files/powered-by-avebot-bot.ave.zone-{}txt{}".format(ctx.message.id, extension)
            await self.bot.download_file(stuff_after, filename)
            if extension != ".jpg" or extension != ".jpeg":
                im = PIL.Image.open(filename)
                new_name = filename.replace(extension, ".jpg")
                im.save(new_name, "JPEG")
                filename = new_name
            images_to_process.append(filename)
        return images_to_process


    async def get_image_links(self, ctx, caller_command):
        image_links = []
        for attach in ctx.message.attachments:
            image_links.append(attach['proxy_url'])
        stuff_after = ctx.message.content.split(caller_command)[1].replace(" ", "")
        if stuff_after != "" and stuff_after.startswith("http"):
            image_links.append(stuff_after)
        return image_links


    @commands.command()
    async def sbahjify(self, ctx):
        """Makes images hella and sweet.

        Usage: ab!sbahjify <link, if you're not uploading an image to discord>"""
        mention = ctx.message.author.mention

        images_to_process = await self.get_images(ctx, "sbahjify")
        msg_to_send = "Processing image(s)." if len(
            images_to_process) != 0 else f"{mention}: No images found."
        "Try linking them or uploading them directly through discord."

        tmp = await ctx.send(msg_to_send)
        for imgtp in images_to_process:
            self.bot.log.info(f"Processing {imgtp} for sbahj")
            im = PIL.Image.open(imgtp)

            for _ in range(2):
                im = PIL.ImageOps.equalize(im)  # Drab-ify, but embellish otherwise hidden artifacts
                im = PIL.ImageOps.solarize(im, 250)  # Create weird blotchy artifacts, but inverts huge swaths
                im = PIL.ImageOps.posterize(im, 2)  # Flatten colors
                for _ in range(2):
                    im = im.filter(PIL.ImageFilter.SHARPEN)
                    im = im.filter(PIL.ImageFilter.SMOOTH)
                    im = im.filter(PIL.ImageFilter.SHARPEN)
            w, h = im.size
            im = im.resize((w, int(h * 0.7)))
            im = PIL.ImageOps.equalize(im)  # Drab-ify, but embellish otherwise hidden artifacts
            im = im.filter(PIL.ImageFilter.SHARPEN)
            im = im.filter(PIL.ImageFilter.SHARPEN)
            out_filename = f"files/sbahjify-{imgtp.replace('files/', '')}"
            im.save(out_filename, quality=0, optimize=False, progressive=False)
            await ctx.send(content=f"{mention}: Here's your image, hella and sweetened:", file=discord.File(out_filename))
        await asyncio.sleep(5)
        await tmp.delete()

    @commands.command()
    async def jpegify(self, ctx):
        """Makes images jpeg. Also check out ab!ultrajpegify.

        Usage: ab!jpegify <link, if you're not uploading an image to discord>"""
        mention = ctx.message.author.mention
        images_to_process = await self.get_images(ctx, "jpegify")

        msg_to_send = "Processing image(s)." if len(
            images_to_process) != 0 else f"{mention}: No images found. Try linking them or uploading them directly through discord."
        tmp = await ctx.send(msg_to_send)
        for imgtp in images_to_process:
            self.bot.log.info(f"Processing {imgtp} for jpeg")
            im = PIL.Image.open(imgtp)

            im = im.filter(PIL.ImageFilter.SHARPEN)
            im = im.filter(PIL.ImageFilter.SMOOTH)
            out_filename = f"files/jpegify-{imgtp.replace('files/', '')}"
            im.save(out_filename, quality=0, optimize=False, progressive=False)
            await ctx.send(content=f"{mention}: Here's your image, jpegified: (also try `ultrajpegify`)", file=discord.File(out_filename))
        await asyncio.sleep(5)
        await tmp.delete()

    @commands.command()
    async def ultrajpegify(self, ctx):
        """Makes images ultra jpeg.

        Usage: ab!ultrajpegify <link, if you're not uploading an image to discord>"""
        mention = ctx.message.author.mention
        images_to_process = await self.get_images(ctx, "ultrajpegify")
        msg_to_send = "Processing image(s)." if len(
            images_to_process) != 0 else f"{mention}: No images found. Try linking them or uploading them directly through discord."
        tmp = await ctx.send(msg_to_send)
        for imgtp in images_to_process:
            self.bot.log.info(f"Processing {imgtp} for new ultrajpeg")
            im = PIL.Image.open(imgtp)
            out_filename = f"files/ultrajpegify-{imgtp.replace('files/', '')}"
            w, h = im.size
            for x in range(0, 25):
                im = im.resize((int(w * 0.9), int(h * 1.1)))
                im.save(out_filename, quality=0, optimize=False, progressive=False)
                im = PIL.Image.open(out_filename)

                im = im.resize((int(w * 1.1), int(h * 0.9)))
                im.save(out_filename, quality=0, optimize=False, progressive=False)
                im = PIL.Image.open(out_filename)
            im = im.resize((w, h))
            im.save(out_filename, quality=0, optimize=False, progressive=False)
            await ctx.send(content=f"{mention}: Here's your image, ULTRA jpegified:", file=discord.File(out_filename))
        await asyncio.sleep(5)
        await tmp.delete()

    @commands.command()
    async def mazeify(self, ctx):
        """Makes images maze-like, with sharpen filter and jpeg abuse.

        Usage: ab!mazeify <link, if you're not uploading an image to discord>"""
        mention = ctx.message.author.mention
        images_to_process = await self.get_images(ctx, "mazeify")
        msg_to_send = "Processing image(s)." if len(
            images_to_process) != 0 else f"{mention}: No images found. Try linking them or uploading them directly through discord."
        tmp = await ctx.send(msg_to_send)
        for imgtp in images_to_process:
            self.bot.log.info(f"Processing {imgtp} for new mazeify")
            im = PIL.Image.open(imgtp)
            out_filename = f"files/mazeify-{imgtp.replace('files/', '')}"

            for x in range(0, 7):
                im = im.filter(PIL.ImageFilter.SHARPEN)
                im.save(out_filename, quality=0, optimize=False, progressive=False)
                im = PIL.Image.open(out_filename)
            await ctx.send(content=f"{mention}: Here's your image, mazeified: (also try `ultramazeify`)", file=discord.File(out_filename))
        await asyncio.sleep(5)
        await tmp.delete()


    @commands.command()
    async def ultramazeify(self, ctx):
        """Makes images ultra maze.

        Usage: ab!ultramazeify <link, if you're not uploading an image to discord>"""
        mention = ctx.message.author.mention
        images_to_process = await self.get_images(ctx, "ultramazeify")
        msg_to_send = "Processing image(s)." if len(
            images_to_process) != 0 else f"{mention}: No images found. Try linking them or uploading them directly through discord."
        tmp = await ctx.send(msg_to_send)
        for imgtp in images_to_process:
            self.bot.log.info(f"Processing {imgtp} for new ultramazeify")
            im = PIL.Image.open(imgtp)
            out_filename = "files/ultramazeify-{}".format(imgtp.replace("files/", ""))

            for x in range(0, 10):
                for y in range(0, 10):
                    im = im.filter(PIL.ImageFilter.SHARPEN)
                im.save(out_filename, quality=0, optimize=False, progressive=False)
                im = PIL.Image.open(out_filename)
            await ctx.send(content=f"{mention}: Here's your image, ULTRA mazeified:", file=discord.File(out_filename))
        await asyncio.sleep(5)
        await tmp.delete()


    @commands.command()
    async def joelify(self, ctx):
        """A tribute to joel (of vinesauce)."""
        mention = ctx.message.author.mention
        images_to_process = await self.get_images(ctx, "joelify")
        msg_to_send = "Processing image(s)." if len(
            images_to_process) != 0 else f"{mention}: No images found. Try linking them or uploading them directly through discord."
        tmp = await ctx.send(msg_to_send)
        for imgtp in images_to_process:
            self.bot.log.info(f"Processing {imgtp} for joelification")
            im = PIL.Image.open(imgtp)
            w, h = im.size

            for i in range(0, 100):
                w_val = (random.randint(1, 20) / 10)
                h_val = (random.randint(1, 20) / 10)
                im = im.resize((int(w * w_val), int(h * h_val)))
                im = im.resize((w, h))

            out_filename = "files/joelify-{}".format(imgtp.replace("files/", ""))
            im.save(out_filename, quality=50, optimize=False, progressive=False)
            await ctx.send(content=f"{mention}: Here's your image, joelified: (also try `ultrajoelify`)", file=discord.File(out_filename))
        await asyncio.sleep(5)
        await tmp.delete()


    @commands.command()
    async def ultrajoelify(self, ctx):
        """A tribute to joel (of vinesauce)."""
        mention = ctx.message.author.mention
        images_to_process = await self.get_images(ctx, "ultrajoelify")
        msg_to_send = "Processing image(s)." if len(
            images_to_process) != 0 else f"{mention}: No images found. Try linking them or uploading them directly through discord."
        tmp = await ctx.send(msg_to_send)
        for imgtp in images_to_process:
            self.bot.log.info(f"Processing {imgtp} for ultra joelification")
            im = PIL.Image.open(imgtp)
            w, h = im.size

            for i in range(0, 500):
                w_val = (random.randint(1, 20) / 10)
                h_val = (random.randint(1, 20) / 10)
                im = im.resize((int(w * w_val), int(h * h_val)))
                im = im.resize((w, h))

            out_filename = "files/joel{}".format(imgtp.replace("files/", ""))
            im.save(out_filename, quality=50, optimize=False, progressive=False)
            await ctx.send(content=f"{mention}: Here's your image, ULTRA joelified:", file=discord.File(out_filename))
        await asyncio.sleep(5)
        await tmp.delete()


    @commands.command(aliases=['giffy', 'gif', 'gifit', 'owo'])
    async def gifify(self, ctx, *the_text: str):
        """Gives a gif image of the text supplied. 

        Example: ab!gifify owo wats this
        Get a specific part in " to have as one image (for example, ab!gifify hi "hi all" heyo will have 3 frames)."""
        mention = ctx.message.author.mention
        fontname = self.bot.config["gifify"]["font"]

        tcount = len(the_text)
        tcurrent = 0
        filenames = ""

        for word in the_text:
            word = word.replace("_", " ")
            tcurrent += 1
            imgsize = 128

            im = PIL.Image.new("RGB", (imgsize, imgsize), color="#343A3B")

            fsize = imgsize
            f = PIL.ImageFont.truetype(fontname, fsize)

            if f.getsize(word)[0] > imgsize:
                fsize = int(fsize/(f.getsize(word)[0] / imgsize))
            f = PIL.ImageFont.truetype(fontname, fsize)

            txt=PIL.Image.new('L', f.getsize(word))
            d = PIL.ImageDraw.Draw(txt)
            d.text((0, 0), word, font=f, fill=255)
            w=txt.rotate(0, expand=1)

            horipos = int((imgsize-f.getsize(word)[0])/2)
            vertpos = int(64-((f.getsize(word)[1]/1.5)))

            im.paste(PIL.ImageOps.colorize(w, (0,0,0), (255,255,255)), (horipos, vertpos), w)
            out_filename = f"gifify/{ctx.message.id}-{tcurrent}.jpg"
            filenames += f"{out_filename} "
            im.save(out_filename, quality=100, optimize=True)
        gif_filename = f"gifify/{ctx.message.id}.gif"
        self.bot.call_shell(f"convert -delay 15 {filenames}gifify/empty.jpg {gif_filename}")
        await ctx.send(content=f"{mention}: here you go", file=discord.File(gif_filename))


    @commands.command()
    async def howold(self, ctx):
        """Guesses age and gender (based on how-old.net)"""
        uri_base = self.bot.config['howold']['uribase']
        subscription_key = self.bot.config['howold']['subkey']
        urls = await self.get_image_links(ctx, "howold")
        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': subscription_key,
        }
        params = {
            'returnFaceId': 'false',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': 'age,gender',
        }
        for url in urls:
            body = {'url': url}
            response = await self.bot.aiosession.post(uri_base + '/face/v1.0/detect', json=body, data=None, headers=headers, params=params)
            response_text = await response.text()
            self.bot.log.info(f"howold response: {response_text}")
            parsed = await response.json()
            try:
                age = parsed[0]["faceAttributes"]["age"]
                gender = parsed[0]["faceAttributes"]["gender"]
                await ctx.send(f"Age: **{age}**\nGender: **{gender}**\n"
                    "(it's hella inaccurate I know blame microsoft not me)")
            except:
                self.bot.log.warning("howold failed: {}".format(traceback.format_exc()))
                await ctx.send("No face detected.")

def setup(bot):
    bot.add_cog(ImageManipulation(bot))
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the `aiojsonrpc` package.
# (c) 2016-2017 Kozlovski Lab <welcome@kozlovskilab.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
:Authors:
    - `Vladimir Kozlovski <vladimir@kozlovskilab.com>`_
"""
import sys
import asyncio

from aiojsonrpc.client import ClientService


async def run():
    client = await ClientService.initialize(amqp_uri='amqp://192.168.100.9')

    # value = await client.run('rpc_queue7', 'wait', 3)
    # print(value)
    # value = await client.run('rpc_queue7', 'wait', 3)
    # print(value)
    # value = await client.run('rpc_queue7', 'wait', 3)
    # print(value)
    # value = await client.run('rpc_queue7', 'wait', 3)
    # print(value)
    # value = await client.run('rpc_queue7', 'wait', 3)
    # print(value)
    # value = await client.run('rpc_queue7', 'wait', 3)
    # print(value)
    # value = await client.run('rpc_queue7', 'wait', 3)
    # print(value)
    # value = await client.run('rpc_queue7', 'wait', 3)
    # print(value)
    # value = await client.run('rpc_queue7', 'wait', 3)
    # print(value)
    # value = await client.run('rpc_queue7', 'wait', 3)
    # print(value)
    # value = await client.run('rpc_queue7', 'wait', 3)
    # print(value)
    # value = await client.run('rpc_queue7', 'wait', 3)
    # print(value)
    #
    # tasks = []
    # tasks.append(client.call('rpc_queue7', 'wait', 3))
    # tasks.append(client.call('rpc_queue7', 'wait', 3))
    # tasks.append(client.call('rpc_queue7', 'wait', 3))
    # tasks.append(client.call('rpc_queue7', 'wait', 3))
    # tasks.append(client.call('rpc_queue7', 'wait', 3))
    # tasks.append(client.call('rpc_queue7', 'wait', 3))
    # tasks.append(client.call('rpc_queue7', 'wait', 3))
    # tasks.append(client.call('rpc_queue7', 'wait', 3))
    # tasks.append(client.call('rpc_queue7', 'wait', 3))
    # tasks.append(client.call('rpc_queue7', 'wait', 3))
    # tasks.append(client.call('rpc_queue7', 'wait', 3))
    # tasks.append(client.call('rpc_queue7', 'wait', 3))
    # await asyncio.wait(tasks)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3058.0 Safari/537.36'
    }
    #await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', parsers=['sitemap'], headers=headers)

    await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.execute('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)


    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/sun-mw0001860258', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/dark-matter-mw0003072847', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/brett-eldredge-mw0003063671', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/lay-it-on-down-mw0003045437', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/louie-louie-louie-mw0003046852', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/claudio-monteverdi-vespro-della-beata-vergine-mw0003030868', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/the-optimist-mw0003042124', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/green-twins-mw0003018254', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/the-counterweight-mw0003023701', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/were-all-alright%21-mw0003046859', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/so-you-wannabe-an-outlaw-mw0003047610', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/marseille-mw0003032005', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/move-upstairs-mw0003036234', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/shake-the-shudder-mw0003036728', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/i-romanticize-mw0003028268', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/rosewood-almanac-mw0003032018', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/dark-matter-mw0003072847', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/brett-eldredge-mw0003063671', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/lay-it-on-down-mw0003045437', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/call-it-love-mw0003067548', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/release/hysteria-3-cd-30th-anniversary-edition-mr0004738868', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/desert-center-mw0003063422', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/yellow-mw0003067955', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/one-of-us-mw0003071155', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/dead-cross-mw0003050396', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/woodland-echoes-mw0003053958', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/were-all-in-this-together-mw0003071058', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/the-fickle-finger-of-fate-mw0003067700', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/pop-voodoo-mw0003050658', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/collection-mw0003056969', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/party-of-one-mw0003065956', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/50000000-elvis-fans-cant-be-wrong-mw0003067840', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/encounters-mw0003064686', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/the-rise-of-chaos-mw0003061917', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/polyphonia-in-excelsis-sacred-music-by-claudio-dallalbero-mw0003048842', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/machaut-sovereign-beauty-mw0003054192', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/stanford-morning-services-in-c-three-motets-lighten-our-darkness-etc-mw0003054193', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/walton-violin-concerto-variations-on-a-theme-by-hindemith-partita-spitfire-prelude-fugue-mw0003054194', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/c%C3%A9sar-franck-sonate-pour-piano-et-violon-ernest-chausson-concert-mw0003053290', headers=headers)
    # await client.run('crawler', 'process', url='http://www.allmusic.com/album/mahler-song-cycles-mw0003061026', headers=headers)




if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(run())
    event_loop.run_forever()
